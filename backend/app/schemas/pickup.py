from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CaregiverNFCRegisterRequest(BaseModel):
    child_id: str = Field(..., example="child-leo-1", description="Child to authorize for caregiver pickup")
    nfc_identifier: str = Field(..., example="CAREGIVER-NFC-001", description="Unique NFC identifier assigned to caregiver badge/card")
    status: Optional[str] = Field("active", example="active")

class CaregiverNFCResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    caregiver_id: str
    child_id: str
    nfc_identifier: str
    status: str = "active"
    last_pickup_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class PickupVerifyRequest(BaseModel):
    child_id: str = Field(..., example="child-leo-1", description="Child being picked up")
    nfc_identifier: str = Field(..., example="CAREGIVER-NFC-001", description="Caregiver's physical NFC badge/card ID")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Caregiver GPS latitude at pickup point")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Caregiver GPS longitude at pickup point")

class PickupVerifyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    verified: bool
    status: str  # PICKUP_VERIFIED, PICKUP_REJECTED, LOCATION_MISMATCH, DEVICE_OFFLINE, UNKNOWN_CAREGIVER_NFC
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    caregiver_id: Optional[str] = None
    caregiver_name: Optional[str] = None
    nfc_identifier: Optional[str] = None
    timestamp: datetime
    location_verified: Optional[bool] = None
    device_verified: Optional[bool] = None
    reason: Optional[str] = None
    safety_event_id: Optional[str] = None
