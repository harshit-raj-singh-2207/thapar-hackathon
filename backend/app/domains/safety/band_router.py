from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.device import (
    BandCreate,
    BandUpdate,
    BandResponse,
    BandStatusResponse,
    BandPairRequest,
    BandPairResponse,
    BandUnpairResponse,
    BandHeartbeatRequest,
    BandHeartbeatResponse,
    BandConnectionResponse,
    BandSyncRequest,
    BandSyncResponse,
    NFCWearableRegisterRequest,
    NFCWearableUpdateRequest,
    NFCVerifyRequest,
    NFCVerifyResponse,
    NFCWearableResponse,
)
from app.domains.safety.gps_band_service import GPSBandService

router = APIRouter(prefix="/bands", tags=["Safety - GPS & NFC Wearable Management"])

# ==========================================
# Standard Band Registration
# ==========================================

@router.post(
    "",
    response_model=BandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register GPS / NFC Band",
    description="Register a new wearable band (with optional NFC/RFID tag) and optionally assign to an authorized child."
)
def register_band(
    data: BandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register band with device identifier, NFC tag ID, battery level, connection status, and optional child assignment.
    """
    service = GPSBandService(db)
    return service.register_band(data=data, current_user=current_user)

# ==========================================
# Dedicated RFID / NFC Wearable Endpoints
# (Registered before generic /{identifier} routes)
# ==========================================

@router.post(
    "/verify-nfc",
    response_model=NFCVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Smart Wearable NFC",
    description="Verify an NFC tag ID and return band status, child association, and semiconductor hardware status."
)
def verify_nfc(
    data: NFCVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify smart wearable NFC tag ID. Returns verified=True with band/child status if registered, or verified=False with reason if unknown.
    """
    service = GPSBandService(db)
    return service.verify_nfc_tag(nfc_tag_id=data.nfc_tag_id, current_user=current_user, allow_unregistered_response=True)

@router.post(
    "/nfc/register",
    response_model=BandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register NFC/RFID Wearable",
    description="Register an NFC/RFID-enabled wearable and securely associate it with a child."
)
def register_nfc_wearable(
    data: NFCWearableRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register NFC wearable with unique NFC tag ID and assign to an authorized child.
    """
    service = GPSBandService(db)
    return service.register_nfc_wearable(data=data, current_user=current_user)

@router.post(
    "/nfc/verify",
    response_model=NFCVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify NFC/RFID Identifier",
    description="Verify that an NFC/RFID identifier exists, is valid, active, and return associated child & band metadata."
)
def verify_nfc_tag_post(
    data: NFCVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify NFC tag identifier via POST body payload.
    """
    service = GPSBandService(db)
    return service.verify_nfc_tag(nfc_tag_id=data.nfc_tag_id, current_user=current_user)

@router.get(
    "/nfc/verify/{nfc_tag_id}",
    response_model=NFCVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify NFC/RFID Identifier (GET)",
    description="Verify that an NFC/RFID identifier exists via path parameter."
)
def verify_nfc_tag_get(
    nfc_tag_id: str = Path(..., description="NFC/RFID tag identifier to verify"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify NFC tag identifier via GET path parameter.
    """
    service = GPSBandService(db)
    return service.verify_nfc_tag(nfc_tag_id=nfc_tag_id, current_user=current_user)

@router.get(
    "/nfc/{nfc_tag_id}",
    response_model=BandResponse,
    summary="Get Wearable by NFC Tag ID",
    description="Retrieve wearable band details using its assigned NFC/RFID identifier."
)
def get_band_by_nfc_tag(
    nfc_tag_id: str = Path(..., description="Unique NFC/RFID tag identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve wearable details by NFC/RFID identifier.
    """
    service = GPSBandService(db)
    return service.get_band_by_nfc(nfc_tag_id=nfc_tag_id, current_user=current_user)

# ==========================================
# Band Connection & Telemetry
# ==========================================

@router.post(
    "/{band_id}/pair",
    response_model=BandPairResponse,
    status_code=status.HTTP_200_OK,
    summary="Pair Band",
    description="Pair a band to a child. Validates child ownership and prevents duplicate pairing."
)
def pair_band(
    band_id: str,
    data: BandPairRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Pair band with child and mark connection status as connected.
    """
    service = GPSBandService(db)
    return service.pair_band(band_id=band_id, child_id=data.child_id, current_user=current_user)

@router.post(
    "/{band_id}/unpair",
    response_model=BandUnpairResponse,
    status_code=status.HTTP_200_OK,
    summary="Unpair Band",
    description="Unpair a band from its current child and update connection status to disconnected."
)
def unpair_band(
    band_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unpair band from current child.
    """
    service = GPSBandService(db)
    return service.unpair_band(band_id=band_id, current_user=current_user)

@router.post(
    "/{band_id}/heartbeat",
    response_model=BandHeartbeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Device Heartbeat",
    description="Receive telemetry from mobile app: update connection status, battery, GPS status, and last seen timestamp."
)
def process_band_heartbeat(
    band_id: str,
    data: BandHeartbeatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process phone/band heartbeat telemetry ping.
    """
    service = GPSBandService(db)
    return service.process_heartbeat(band_id=band_id, data=data, current_user=current_user)

@router.get(
    "/{band_id}/connection",
    response_model=BandConnectionResponse,
    summary="Get Connection Status",
    description="Retrieve live connection status, battery percentage, GPS status, last seen, and stale status."
)
def get_band_connection(
    band_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get live connection status, paired state, battery, and check if device is stale.
    """
    service = GPSBandService(db)
    return service.get_connection_status(band_id=band_id, current_user=current_user)

@router.post(
    "/{band_id}/sync",
    response_model=BandSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Device Synchronization",
    description="Synchronize device settings and refresh device synchronization state."
)
def sync_band(
    band_id: str,
    data: BandSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Synchronize phone and band configuration and timestamps.
    """
    service = GPSBandService(db)
    return service.sync_band(band_id=band_id, data=data, current_user=current_user)

@router.get(
    "/{band_id}/status",
    response_model=BandStatusResponse,
    summary="Get Band Status",
    description="Retrieve live hardware status, battery percentage, GPS status, NFC tag ID, and last seen timestamp."
)
def get_band_status(
    band_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get band online/offline status, battery level, GPS status, and last seen timestamp.
    """
    service = GPSBandService(db)
    return service.get_band_status(band_id=band_id, current_user=current_user)

# ==========================================
# NFC Tag Update Specific Endpoints
# ==========================================

@router.put(
    "/{band_id}/nfc",
    response_model=BandResponse,
    summary="Update NFC Identifier (PUT)",
    description="Update or assign an NFC/RFID tag identifier to an existing wearable band."
)
@router.patch(
    "/{band_id}/nfc",
    response_model=BandResponse,
    summary="Update NFC Identifier (PATCH)",
    description="Update or assign an NFC/RFID tag identifier to an existing wearable band."
)
def update_band_nfc_tag(
    band_id: str,
    data: NFCWearableUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update NFC/RFID identifier for an existing wearable band.
    """
    service = GPSBandService(db)
    return service.update_nfc_tag(band_id=band_id, nfc_tag_id=data.nfc_tag_id, current_user=current_user)

# ==========================================
# Generic Band CRUD by ID or Child ID
# ==========================================

@router.get(
    "/{identifier}",
    response_model=BandResponse,
    summary="Get Band Details or Child's Band",
    description="Retrieve band details by band ID, NFC tag ID, or get the band assigned to a child by child ID."
)
def get_band(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get band details by band ID, NFC tag ID, or get child's band by child ID.
    Only authorized caregivers can view the band.
    """
    service = GPSBandService(db)
    return service.get_band_by_identifier(identifier=identifier, current_user=current_user)

@router.patch(
    "/{band_id}",
    response_model=BandResponse,
    summary="Update Band",
    description="Update GPS/NFC band configuration, status, battery level, NFC tag ID, or child assignment."
)
def update_band(
    band_id: str,
    data: BandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update band details. Prevents duplicate child assignment, duplicate NFC IDs, and ensures caregiver authorization.
    """
    service = GPSBandService(db)
    return service.update_band(band_id=band_id, data=data, current_user=current_user)

@router.delete(
    "/{band_id}",
    summary="Remove Band",
    description="Remove/unpair a GPS/NFC band."
)
def remove_band(
    band_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove or unpair a GPS/NFC band.
    """
    service = GPSBandService(db)
    return service.remove_band(band_id=band_id, current_user=current_user)
