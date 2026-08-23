from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.pickup import (
    CaregiverNFCRegisterRequest,
    CaregiverNFCResponse,
    PickupVerifyRequest,
    PickupVerifyResponse,
)
from app.domains.safety.pickup_service import CaregiverPickupService

router = APIRouter(tags=["Safety - Caregiver NFC & Authorized Pickup"])

@router.post(
    "/caregiver/nfc/register",
    response_model=CaregiverNFCResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Caregiver NFC Identifier",
    description="Register an authorized physical NFC badge identifier for a caregiver to pick up a specific child."
)
@router.post(
    "/caregiver/nfc/register/",
    response_model=CaregiverNFCResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def register_caregiver_nfc(
    data: CaregiverNFCRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register caregiver NFC tag ID. Enforces caregiver authorization, child association, and NFC uniqueness.
    """
    service = CaregiverPickupService(db)
    return service.register_caregiver_nfc(data=data, current_user=current_user)

@router.post(
    "/pickup/verify",
    response_model=PickupVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Authorized Caregiver Pickup",
    description="Verifies caregiver pickup combining caregiver NFC identity, authorized child match, GPS proximity, and child wearable status."
)
@router.post(
    "/pickup/verify/",
    response_model=PickupVerifyResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
def verify_pickup(
    data: PickupVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Multi-signal pickup verification combining:
    1. Caregiver NFC Identity
    2. Caregiver Child Authorization
    3. GPS Proximity to Allowed Pickup Zone
    4. Child Smart Wearable Online & Battery State
    """
    service = CaregiverPickupService(db)
    return service.verify_pickup(data=data, current_user=current_user)
