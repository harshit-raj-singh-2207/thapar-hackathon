from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.safety_event import SafetyEvent
from app.schemas.safety_event import (
    SafetyEventCreate,
    SafetyEventResponse,
    SafetyEventAcknowledge,
)

router = APIRouter(prefix="/safety-events", tags=["Safety - Audit & Event Logs"])

@router.get("/", response_model=List[SafetyEventResponse])
def list_safety_events(
    child_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    is_acknowledged: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List safety and security events (breaches, separation alerts, SOS, low battery).
    """
    user_child_ids = [c.id for c in current_user.children]
    query = db.query(SafetyEvent)

    if child_id:
        query = query.filter(SafetyEvent.child_id == child_id)
    elif user_child_ids:
        query = query.filter(SafetyEvent.child_id.in_(user_child_ids))

    if event_type:
        query = query.filter(SafetyEvent.event_type == event_type)
    if is_acknowledged is not None:
        query = query.filter(SafetyEvent.is_acknowledged == is_acknowledged)

    return query.order_by(SafetyEvent.created_at.desc()).limit(limit).all()

@router.post("/{event_id}/acknowledge", response_model=SafetyEventResponse)
def acknowledge_safety_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a safety alert or event as acknowledged by the caregiver.
    """
    event = db.query(SafetyEvent).filter(SafetyEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Safety event not found.")

    event.is_acknowledged = True
    event.acknowledged_at = datetime.now(timezone.utc)
    event.acknowledged_by = current_user.id
    db.commit()
    db.refresh(event)
    return event
