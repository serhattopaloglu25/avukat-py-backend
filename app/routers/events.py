"""Event management routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_current_org

router = APIRouter()

@router.get("/", response_model=List[schemas.EventResponse])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    q: Optional[str] = None,
    upcoming: Optional[bool] = None,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """List all events for the current organization"""
    query = db.query(models.Event).options(
        joinedload(models.Event.case).joinedload(models.Case.client)
    ).filter(
        models.Event.org_id == current_org.id
    )
    
    # Search filter
    if q:
        query = query.filter(
            models.Event.title.contains(q) |
            models.Event.location.contains(q)
        )
    
    # Upcoming filter
    if upcoming:
        query = query.filter(models.Event.starts_at >= datetime.utcnow())
    
    # Order by start date
    query = query.order_by(models.Event.starts_at)
    
    events = query.offset(skip).limit(limit).all()
    return events

@router.post("/", response_model=schemas.EventResponse)
async def create_event(
    event_data: schemas.EventCreate,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Create a new event"""
    # If case_id is provided, verify it belongs to org
    if event_data.case_id:
        case = db.query(models.Case).filter(
            models.Case.id == event_data.case_id,
            models.Case.org_id == current_org.id
        ).first()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Case not found or doesn't belong to your organization"
            )
    
    new_event = models.Event(
        user_id=current_user.id,
        org_id=current_org.id,
        **event_data.dict()
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    # Load relationships
    new_event = db.query(models.Event).options(
        joinedload(models.Event.case).joinedload(models.Case.client)
    ).filter(models.Event.id == new_event.id).first()
    
    return new_event

@router.get("/{event_id}", response_model=schemas.EventResponse)
async def get_event(
    event_id: int,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Get a specific event"""
    event = db.query(models.Event).options(
        joinedload(models.Event.case).joinedload(models.Case.client)
    ).filter(
        models.Event.id == event_id,
        models.Event.org_id == current_org.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event

@router.put("/{event_id}", response_model=schemas.EventResponse)
async def update_event(
    event_id: int,
    event_data: schemas.EventUpdate,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Update an event"""
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.org_id == current_org.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # If updating case_id, verify it belongs to org
    if event_data.case_id is not None:
        if event_data.case_id:  # If not None and not 0
            case = db.query(models.Case).filter(
                models.Case.id == event_data.case_id,
                models.Case.org_id == current_org.id
            ).first()
            
            if not case:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Case not found or doesn't belong to your organization"
                )
    
    # Update fields
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    # Load relationships
    event = db.query(models.Event).options(
        joinedload(models.Event.case).joinedload(models.Case.client)
    ).filter(models.Event.id == event_id).first()
    
    return event

@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Delete an event"""
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.org_id == current_org.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}
