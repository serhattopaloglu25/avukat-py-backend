from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse, EventUpdate
from app.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[EventResponse])
async def get_events(
    q: Optional[str] = Query(None, description="Search query"),
    case_id: Optional[int] = Query(None, description="Filter by case"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.org_id == current_user.current_org_id)
    
    if q:
        query = query.filter(Event.title.ilike(f"%{q}%"))
    
    if case_id:
        query = query.filter(Event.case_id == case_id)
    
    if start_date:
        query = query.filter(Event.starts_at >= start_date)
    
    if end_date:
        query = query.filter(Event.starts_at <= end_date)
    
    events = query.order_by(Event.starts_at).offset(skip).limit(limit).all()
    return events

@router.post("/", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.current_org_id:
        raise HTTPException(status_code=400, detail="User not in any organization")
    
    event = Event(
        **event_data.dict(),
        user_id=current_user.id,
        org_id=current_user.current_org_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.org_id == current_user.current_org_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.org_id == current_user.current_org_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.org_id == current_user.current_org_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}
