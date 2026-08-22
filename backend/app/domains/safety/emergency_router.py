from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.emergency import (
    SOSTriggerRequest,
    EmergencyResolveRequest,
    EmergencyResponse,
    EmergencyDetailResponse,
)
from app.domains.safety.emergency_service import EmergencyService

router = APIRouter(prefix="/emergency", tags=["Safety - SOS & Emergency System"])

@router.post(
    "/sos",
    response_model=EmergencyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger SOS Emergency",
    description="Trigger a critical SOS emergency. Automatically captures location, prevents duplicates, creates safety events and dispatches caregiver alerts."
)
def trigger_sos(
    data: SOSTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger an SOS emergency.
    """
    service = EmergencyService(db)
    return service.trigger_sos(data=data, current_user=current_user)

@router.get(
    "/{event_id}/details",
    response_model=EmergencyDetailResponse,
    summary="Get Emergency Details",
    description="Get comprehensive details for an emergency event."
)
def get_emergency_details(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed emergency event information.
    """
    service = EmergencyService(db)
    return service.get_emergency_details(event_id=event_id, current_user=current_user)

@router.post(
    "/{event_id}/resolve",
    response_model=EmergencyResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve Emergency",
    description="Resolve an active emergency and restore child status to safe."
)
def resolve_emergency(
    event_id: str,
    data: Optional[EmergencyResolveRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resolve an active emergency.
    """
    service = EmergencyService(db)
    return service.resolve_emergency(event_id=event_id, data=data, current_user=current_user)

@router.get(
    "/{child_id}",
    response_model=EmergencyDetailResponse,
    summary="Get Child Emergency Status",
    description="Get active or most recent emergency information for a child."
)
def get_child_emergency(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get child's active or latest emergency information.
    """
    service = EmergencyService(db)
    return service.get_child_emergency(child_id=child_id, current_user=current_user)
