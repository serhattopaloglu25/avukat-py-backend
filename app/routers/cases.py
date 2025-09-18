from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseResponse, CaseUpdate
from app.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CaseResponse])
async def get_cases(
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Case).filter(Case.org_id == current_user.current_org_id)
    
    if q:
        query = query.filter(
            (Case.title.ilike(f"%{q}%")) | 
            (Case.case_no.ilike(f"%{q}%"))
        )
    
    if status:
        query = query.filter(Case.status == status)
    
    cases = query.offset(skip).limit(limit).all()
    return cases

@router.post("/", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.current_org_id:
        raise HTTPException(status_code=400, detail="User not in any organization")
    
    # Check if case_no already exists
    existing = db.query(Case).filter(Case.case_no == case_data.case_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="Case number already exists")
    
    case = Case(
        **case_data.dict(),
        user_id=current_user.id,
        org_id=current_user.current_org_id
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.org_id == current_user.current_org_id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.org_id == current_user.current_org_id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check case_no uniqueness if updating
    if case_data.case_no and case_data.case_no != case.case_no:
        existing = db.query(Case).filter(Case.case_no == case_data.case_no).first()
        if existing:
            raise HTTPException(status_code=400, detail="Case number already exists")
    
    for key, value in case_data.dict(exclude_unset=True).items():
        setattr(case, key, value)
    
    db.commit()
    db.refresh(case)
    return case

@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.org_id == current_user.current_org_id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(case)
    db.commit()
    return {"message": "Case deleted successfully"}
