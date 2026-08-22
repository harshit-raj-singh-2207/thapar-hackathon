from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.separation import (
    SeparationEvaluationResponse,
    SeparationStatusResponse,
    SeparationResolveResponse,
)
from app.domains.safety.separation_service import SeparationDomainService

router = APIRouter(prefix="/separation", tags=["Safety - Separation Detection"])

@router.get(
    "/{child_id}/status",
    response_model=SeparationStatusResponse,
    summary="Get Separation Status",
    description="Retrieve live separation status summary, distance, connection status, and active alert state."
)
def get_separation_status(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get concise separation status for an authorized child.
    """
    service = SeparationDomainService(db)
    return service.get_separation_status(child_id=child_id, current_user=current_user)

@router.get(
    "/{child_id}",
    response_model=SeparationEvaluationResponse,
    summary="Evaluate Separation",
    description="Evaluate separation triggers (band disconnected, heartbeat timeout, distance threshold) and generate alerts/events if breached."
)
def evaluate_separation(
    child_id: str,
    caregiver_lat: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Caregiver current latitude"),
    caregiver_lon: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Caregiver current longitude"),
    threshold_meters: Optional[float] = Query(None, ge=1.0, description="Custom distance threshold in meters"),
    heartbeat_timeout_seconds: Optional[int] = Query(None, ge=1, description="Custom heartbeat timeout in seconds"),
    create_event: bool = Query(True, description="Whether to persist a safety event when separation is detected"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate child separation status and trigger safety events when breached.
    """
    service = SeparationDomainService(db)
    return service.evaluate_separation(
        child_id=child_id,
        current_user=current_user,
        caregiver_lat=caregiver_lat,
        caregiver_lon=caregiver_lon,
        custom_threshold_meters=threshold_meters,
        custom_heartbeat_timeout_seconds=heartbeat_timeout_seconds,
        create_event=create_event,
    )

@router.post(
    "/{child_id}/resolve",
    response_model=SeparationResolveResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve Separation Event",
    description="Acknowledge and resolve active separation events for the child, restoring safe status."
)
def resolve_separation(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resolve active separation events for the child.
    """
    service = SeparationDomainService(db)
    return service.resolve_separation(child_id=child_id, current_user=current_user)
