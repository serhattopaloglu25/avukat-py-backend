"""Statistics routes"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_current_org

router = APIRouter()

@router.get("/", response_model=schemas.StatsResponse)
async def get_stats(
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Get statistics for the current organization"""
    # Count total clients
    total_clients = db.query(models.Client).filter(
        models.Client.org_id == current_org.id
    ).count()
    
    # Count total cases
    total_cases = db.query(models.Case).filter(
        models.Case.org_id == current_org.id
    ).count()
    
    # Count active cases
    active_cases = db.query(models.Case).filter(
        models.Case.org_id == current_org.id,
        models.Case.status == models.CaseStatusEnum.active
    ).count()
    
    # Count upcoming events
    upcoming_events = db.query(models.Event).filter(
        models.Event.org_id == current_org.id,
        models.Event.starts_at >= datetime.utcnow()
    ).count()
    
    return {
        "total_clients": total_clients,
        "total_cases": total_cases,
        "active_cases": active_cases,
        "upcoming_events": upcoming_events
    }
