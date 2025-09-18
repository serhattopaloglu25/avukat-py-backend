"""Case management routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_current_org

router = APIRouter()

@router.get("/", response_model=List[schemas.CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    q: Optional[str] = None,
    status: Optional[schemas.CaseStatusEnum] = None,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """List all cases for the current organization"""
    query = db.query(models.Case).options(
        joinedload(models.Case.client)
    ).filter(
        models.Case.org_id == current_org.id
    )
    
    # Search filter
    if q:
        query = query.filter(
            models.Case.title.contains(q) |
            models.Case.case_number.contains(q)
        )
    
    # Status filter
    if status:
        query = query.filter(models.Case.status == status)
    
    cases = query.offset(skip).limit(limit).all()
    return cases

@router.post("/", response_model=schemas.CaseResponse)
async def create_case(
    case_data: schemas.CaseCreate,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Create a new case"""
    # Verify client belongs to org
    client = db.query(models.Client).filter(
        models.Client.id == case_data.client_id,
        models.Client.org_id == current_org.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client not found or doesn't belong to your organization"
        )
    
    # Check if case number already exists
    existing_case = db.query(models.Case).filter(
        models.Case.case_number == case_data.case_number
    ).first()
    
    if existing_case:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case number already exists"
        )
    
    new_case = models.Case(
        user_id=current_user.id,
        org_id=current_org.id,
        **case_data.dict()
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    # Load client relationship
    new_case = db.query(models.Case).options(
        joinedload(models.Case.client)
    ).filter(models.Case.id == new_case.id).first()
    
    return new_case

@router.get("/{case_id}", response_model=schemas.CaseResponse)
async def get_case(
    case_id: int,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Get a specific case"""
    case = db.query(models.Case).options(
        joinedload(models.Case.client)
    ).filter(
        models.Case.id == case_id,
        models.Case.org_id == current_org.id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return case

@router.put("/{case_id}", response_model=schemas.CaseResponse)
async def update_case(
    case_id: int,
    case_data: schemas.CaseUpdate,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Update a case"""
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.org_id == current_org.id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # If updating client_id, verify it belongs to org
    if case_data.client_id:
        client = db.query(models.Client).filter(
            models.Client.id == case_data.client_id,
            models.Client.org_id == current_org.id
        ).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found or doesn't belong to your organization"
            )
    
    # If updating case_number, check uniqueness
    if case_data.case_number and case_data.case_number != case.case_number:
        existing_case = db.query(models.Case).filter(
            models.Case.case_number == case_data.case_number
        ).first()
        
        if existing_case:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case number already exists"
            )
    
    # Update fields
    update_data = case_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    
    # Load relationships
    case = db.query(models.Case).options(
        joinedload(models.Case.client)
    ).filter(models.Case.id == case_id).first()
    
    return case

@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Delete a case"""
    case = db.query(models.Case).filter(
        models.Case.id == case_id,
        models.Case.org_id == current_org.id
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    db.delete(case)
    db.commit()
    
    return {"message": "Case deleted successfully"}
