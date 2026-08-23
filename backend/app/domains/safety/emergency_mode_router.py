from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.emergency_mode import (
    EmergencyModeCreate,
    EmergencyModeUpdate,
    EmergencyModeResponse,
    EmergencyDashboardSummaryResponse,
    NFCEmergencyCardResponse,
)
from app.domains.safety.emergency_mode_service import EmergencyModeService

router = APIRouter(prefix="/emergency", tags=["Safety - 90-Day Emergency Support Mode"])

@router.post(
    "/mode",
    response_model=EmergencyModeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Activate / Create 90-Day Emergency Mode",
    description="Enable home-bound emergency support mode for a child, setting custom duration, reason, and support preferences.",
)
@router.post(
    "/mode/",
    response_model=EmergencyModeResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_emergency_mode(
    data: EmergencyModeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create or update the emergency mode configuration for a specific child.
    Validates caregiver ownership and date constraints.
    """
    service = EmergencyModeService(db)
    return service.create_emergency_mode(data=data, current_user=current_user)


@router.get(
    "/mode/{child_id}",
    response_model=EmergencyModeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Child Emergency Mode Status",
    description="Retrieve the active emergency mode details, days remaining, and support preferences for a child.",
)
def get_emergency_mode(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current emergency mode status for a child.
    """
    service = EmergencyModeService(db)
    return service.get_emergency_mode(child_id=child_id, current_user=current_user)


@router.patch(
    "/mode/{child_id}",
    response_model=EmergencyModeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Emergency Mode Configuration",
    description="Update emergency mode active state, duration, end date, reason, or individual support preferences.",
)
def update_emergency_mode(
    child_id: str,
    data: EmergencyModeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing emergency mode for a child.
    """
    service = EmergencyModeService(db)
    return service.update_emergency_mode(child_id=child_id, data=data, current_user=current_user)


@router.get(
    "/dashboard/{child_id}",
    response_model=EmergencyDashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Emergency Dashboard Summary",
    description="Aggregates child status, communication, learning, emotional support, and safety telemetry into a single remote caregiver dashboard payload.",
)
def get_emergency_dashboard(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get unified emergency dashboard summary for remote caregiver oversight.
    """
    service = EmergencyModeService(db)
    return service.get_emergency_dashboard(child_id=child_id, current_user=current_user)


@router.get(
    "/nfc-card/{nfc_tag_id}",
    response_model=NFCEmergencyCardResponse,
    status_code=status.HTTP_200_OK,
    summary="NFC Safe Emergency Identification Card",
    description="Public identification pass when an autistic child's NFC band is tapped during an emergency or separation.",
)
@router.get(
    "/nfc/emergency-card/{nfc_tag_id}",
    response_model=NFCEmergencyCardResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def get_nfc_emergency_card(
    nfc_tag_id: str,
    db: Session = Depends(get_db),
):
    """
    Public safe identification card endpoint for NFC band tap.
    Returns primary caregiver and emergency contacts with autism-friendly instructions,
    without exposing sensitive GPS breadcrumbs.
    """
    service = EmergencyModeService(db)
    return service.get_nfc_emergency_card(nfc_tag_id=nfc_tag_id)

