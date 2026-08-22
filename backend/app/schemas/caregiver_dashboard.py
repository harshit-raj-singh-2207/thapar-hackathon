import json
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChildProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
    autism_level: Optional[str] = None
    medical_notes: Optional[str] = None
    caregiver_id: str
    caregiver_name: Optional[str] = None
    account_status: str = "active"
    tracking_enabled: bool = True
    current_status: str = "safe"
    created_at: datetime
    updated_at: Optional[datetime] = None

class ChildStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_id: str
    name: str
    current_status: str = "safe"
    is_online: bool = False
    location_available: bool = False
    last_known_location: Optional[Dict[str, Any]] = None
    gps_status: str = "inactive"
    gps_accuracy: Optional[float] = None
    last_location_update: Optional[datetime] = None
    band_connection_status: str = "none"
    is_separated: bool = False
    safe_zone_status: str = "no_zones"
    emergency_status: str = "none"
    active_emergency_id: Optional[str] = None

class ChildLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None
    recorded_at: Optional[datetime] = None
    source: Optional[str] = None
    is_live: bool = False
    location_available: bool = False
    status: str = "unavailable"  # fresh, stale, unavailable

class DeviceStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    band_id: Optional[str] = None
    device_identifier: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    connection_status: str = "none"
    is_online: bool = False
    is_paired: bool = False
    battery_level: Optional[int] = None
    battery_status: str = "unknown"  # good, low, critical, unknown
    gps_status: str = "unknown"
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    is_stale: bool = False

class RecentActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    child_id: str
    event_type: str
    severity: str
    title: str
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    is_acknowledged: bool = False
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_metadata(cls, data: Any) -> Any:
        if hasattr(data, "metadata_json"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                meta_raw = data_dict.get("metadata_json")
                if meta_raw and isinstance(meta_raw, str):
                    try:
                        data_dict["metadata"] = json.loads(meta_raw)
                    except Exception:
                        data_dict["metadata"] = None
                return data_dict
            except Exception:
                pass
        return data

class AlertSummaryResponse(BaseModel):
    child_id: str
    total_alerts: int = 0
    unread_alerts: int = 0
    active_alerts: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    warning_alerts: int = 0
    info_alerts: int = 0

class SafetyOverviewResponse(BaseModel):
    child: ChildProfileResponse
    location: ChildLocationResponse
    device: DeviceStatusResponse
    safety: Dict[str, Any]
    emergency: Dict[str, Any]
    alerts: Dict[str, Any]
    events: List[RecentActivityItem]
