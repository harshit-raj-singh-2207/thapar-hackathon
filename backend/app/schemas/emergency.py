from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Any
from datetime import datetime

class EmergencyCreate(BaseModel):
    child_id: str
    triggered_by: str = Field("sos_button", example="sos_button")
    severity: str = Field("critical", example="critical")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    message: Optional[str] = "Emergency SOS button pressed!"

class SOSTriggerRequest(BaseModel):
    child_id: str = Field(..., example="child-leo-1", description="Target child ID")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Optional current GPS latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Optional current GPS longitude")
    message: Optional[str] = Field(None, example="SOS Button Pressed by Leo")
    description: Optional[str] = Field(None, example="Immediate assistance required")
    triggered_by: Optional[str] = Field("sos_button", example="sos_button")

    @model_validator(mode="before")
    @classmethod
    def sync_message(cls, data: Any) -> Any:
        if isinstance(data, dict):
            msg = data.get("message") or data.get("description") or "Emergency SOS Triggered!"
            data["message"] = msg
            data["description"] = msg
        return data

class EmergencyResolveRequest(BaseModel):
    status: str = Field("resolved", example="resolved")  # resolved, false_alarm
    resolution_notes: Optional[str] = "Child found safe and sound."

class EmergencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: str
    caregiver_id: Optional[str] = None
    status: str = "active"
    severity: str = "critical"
    triggered_by: str = "sos_button"
    event_type: str = "SOS"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_available: bool = False
    address: Optional[str] = None
    message: Optional[str] = None
    description: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    triggered_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if hasattr(data, "child_id"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                lat = data_dict.get("latitude")
                lon = data_dict.get("longitude")
                msg = data_dict.get("message") or "Emergency SOS Triggered!"
                created = data_dict.get("created_at") or datetime.now()

                data_dict["location_available"] = lat is not None and lon is not None
                data_dict["message"] = msg
                data_dict["description"] = msg
                data_dict["event_type"] = "SOS"
                data_dict["triggered_at"] = created
                data_dict["created_at"] = created
                return data_dict
            except Exception:
                pass
        return data

class EmergencyDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: str
    caregiver_id: Optional[str] = None
    status: str = "active"
    severity: str = "critical"
    triggered_by: str = "sos_button"
    event_type: str = "SOS"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_available: bool = False
    location_timestamp: Optional[datetime] = None
    location_source: Optional[str] = None
    address: Optional[str] = None
    message: Optional[str] = None
    description: Optional[str] = None
    triggered_at: datetime
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_detail_aliases(cls, data: Any) -> Any:
        if hasattr(data, "child_id"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                lat = data_dict.get("latitude")
                lon = data_dict.get("longitude")
                msg = data_dict.get("message") or "Emergency SOS Triggered!"
                created = data_dict.get("created_at") or datetime.now()

                data_dict["location_available"] = lat is not None and lon is not None
                data_dict["message"] = msg
                data_dict["description"] = msg
                data_dict["event_type"] = "SOS"
                data_dict["triggered_at"] = created
                data_dict["created_at"] = created
                data_dict["location_timestamp"] = created if lat is not None else None
                data_dict["location_source"] = "gps" if lat is not None else None
                return data_dict
            except Exception:
                pass
        return data
