from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Client, Case, Event
from app.schemas import StatsResponse
from app.deps import get_current_user

router = APIRouter()

@router.get("/stats", response_model=StatsResponse)
async def get_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.current_org_id:
        return {
            "total_clients": 0,
            "total_cases": 0, 
            "active_cases": 0,
            "upcoming_events": 0
        }
    
    total_clients = db.query(Client).filter(
        Client.org_id == current_user.current_org_id
    ).count()
    
    total_cases = db.query(Case).filter(
        Case.org_id == current_user.current_org_id
    ).count()
    
    active_cases = db.query(Case).filter(
        Case.org_id == current_user.current_org_id,
        Case.status == "active"
    ).count()
    
    # Upcoming events (next 30 days)
    upcoming_events = db.query(Event).filter(
        Event.org_id == current_user.current_org_id,
        Event.starts_at >= datetime.now(),
        Event.starts_at <= datetime.now() + timedelta(days=30)
    ).count()
    
    return {
        "total_clients": total_clients,
        "total_cases": total_cases,
        "active_cases": active_cases,
        "upcoming_events": upcoming_events
    }

@router.get("/dashboard/stats")
async def dashboard_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Alias for stats endpoint"""
    return await get_stats(current_user, db)
