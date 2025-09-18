"""Client management routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_current_org

router = APIRouter()

@router.get("/", response_model=List[schemas.ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    q: Optional[str] = None,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """List all clients for the current organization"""
    query = db.query(models.Client).filter(
        models.Client.org_id == current_org.id
    )
    
    # Search filter
    if q:
        query = query.filter(
            models.Client.name.contains(q) |
            models.Client.email.contains(q) |
            models.Client.phone.contains(q)
        )
    
    clients = query.offset(skip).limit(limit).all()
    return clients

@router.post("/", response_model=schemas.ClientResponse)
async def create_client(
    client_data: schemas.ClientCreate,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Create a new client"""
    new_client = models.Client(
        user_id=current_user.id,
        org_id=current_org.id,
        **client_data.dict()
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@router.get("/{client_id}", response_model=schemas.ClientResponse)
async def get_client(
    client_id: int,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Get a specific client"""
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.org_id == current_org.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client

@router.put("/{client_id}", response_model=schemas.ClientResponse)
async def update_client(
    client_id: int,
    client_data: schemas.ClientUpdate,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Update a client"""
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.org_id == current_org.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update fields
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Delete a client"""
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.org_id == current_org.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db.delete(client)
    db.commit()
    
    return {"message": "Client deleted successfully"}
