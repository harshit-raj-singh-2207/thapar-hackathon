from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.safe_zone import (
    CheckpointCreate,
    CheckpointResponse,
    NFCGPSVerifyRequest,
    NFCGPSVerifyResponse,
)
from app.domains.safety.smart_verification_service import SmartVerificationService

router = APIRouter(tags=["Safety - Smart Checkpoints & Multi-Signal Verification"])

# ==============================================================================
# NFC Checkpoint Endpoints
# ==============================================================================

@router.post(
    "/checkpoints",
    response_model=CheckpointResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create NFC Checkpoint",
    description="Create a physical NFC checkpoint/safe point with geolocation and proximity radius."
)
@router.post(
    "/checkpoints/",
    response_model=CheckpointResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_checkpoint(
    data: CheckpointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register a new NFC checkpoint. Validates NFC tag uniqueness and coordinate validity.
    """
    service = SmartVerificationService(db)
    return service.create_checkpoint(data=data, current_user=current_user)

@router.get(
    "/checkpoints",
    response_model=List[CheckpointResponse],
    summary="List NFC Checkpoints",
    description="List all NFC checkpoints accessible to the current caregiver."
)
@router.get(
    "/checkpoints/",
    response_model=List[CheckpointResponse],
    include_in_schema=False
)
def list_checkpoints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all registered NFC checkpoints.
    """
    service = SmartVerificationService(db)
    return service.list_checkpoints(current_user=current_user)

@router.get(
    "/checkpoints/nfc/{nfc_tag_id}",
    response_model=CheckpointResponse,
    summary="Get Checkpoint by NFC Tag ID",
    description="Retrieve checkpoint metadata by scanning its unique NFC tag ID."
)
def get_checkpoint_by_nfc(
    nfc_tag_id: str = Path(..., description="Unique NFC tag identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lookup checkpoint details using its physical NFC tag ID.
    """
    service = SmartVerificationService(db)
    return service.get_checkpoint(identifier=nfc_tag_id, current_user=current_user)

@router.get(
    "/checkpoints/{checkpoint_id}",
    response_model=CheckpointResponse,
    summary="Get Checkpoint by ID",
    description="Retrieve checkpoint metadata using its primary ID or tag."
)
def get_checkpoint_by_id(
    checkpoint_id: str = Path(..., description="Checkpoint ID or identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lookup checkpoint details by identifier.
    """
    service = SmartVerificationService(db)
    return service.get_checkpoint(identifier=checkpoint_id, current_user=current_user)

# ==============================================================================
# Multi-Signal Smart Safety Verification Endpoint (NFC + GPS + Device Status)
# ==============================================================================

@router.post(
    "/verification/nfc-gps",
    response_model=NFCGPSVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Multi-Signal NFC + GPS Safety Verification",
    description="Verifies child presence combining NFC checkpoint identity, GPS distance radius, and wearable semiconductor status."
)
@router.post(
    "/verification/nfc-gps/",
    response_model=NFCGPSVerifyResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
def verify_nfc_gps(
    data: NFCGPSVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify child safety using three combined signals:
    1. NFC Checkpoint Tag ID
    2. GPS Location within Checkpoint Radius
    3. Active Semiconductor Wearable Telemetry (Battery, Online state, BLE)
    """
    service = SmartVerificationService(db)
    return service.verify_nfc_gps(data=data, current_user=current_user)
