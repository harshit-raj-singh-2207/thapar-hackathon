from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime

class SafetyEventCreate(BaseModel):
    child_id: str
    event_type: str = Field(..., example="geofence_exit")
    severity: str = Field("warning", example="warning")
    title: str = Field(..., example="Safe Zone Exit Detected")
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata_json: Optional[str] = None

class SafetyEventAcknowledge(BaseModel):
    acknowledged: bool = True

class SafetyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    child_id: str
    event_type: str
    severity: str
    title: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata_json: Optional[str] = None
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    created_at: datetime

class SafetyOverviewSummary(BaseModel):
    child_id: str
    child_name: str
    status: str
    is_safe: bool
    battery_level: int
    last_known_location: Optional[dict] = None
    active_safe_zones_count: int
    unacknowledged_alerts_count: int
    active_emergency_count: int
    is_device_online: bool
