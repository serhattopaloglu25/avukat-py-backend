from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Client
from app.schemas import ClientCreate, ClientResponse, ClientUpdate
from app.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    q: Optional[str] = Query(None, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Client).filter(Client.org_id == current_user.current_org_id)
    
    if q:
        query = query.filter(Client.name.ilike(f"%{q}%"))
    
    clients = query.offset(skip).limit(limit).all()
    return clients

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.current_org_id:
        raise HTTPException(status_code=400, detail="User not in any organization")
    
    client = Client(
        **client_data.dict(),
        user_id=current_user.id,
        org_id=current_user.current_org_id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.org_id == current_user.current_org_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.org_id == current_user.current_org_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    for key, value in client_data.dict(exclude_unset=True).items():
        setattr(client, key, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.org_id == current_user.current_org_id
    ).first()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    return {"message": "Client deleted successfully"}
