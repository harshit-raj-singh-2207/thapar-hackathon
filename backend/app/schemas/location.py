from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Any
from datetime import datetime

class LocationCreate(BaseModel):
    child_id: str = Field(..., description="Child unique identifier")
    device_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate between -180 and 180")
    accuracy: Optional[float] = Field(5.0, ge=0.0, description="GPS Accuracy in meters (must be >= 0)")
    source: Optional[str] = Field("gps", description="Location source: gps, device, network, or manual")
    altitude: Optional[float] = None
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    battery_level: Optional[float] = None
    address: Optional[str] = None
    recorded_at: Optional[datetime] = None
    timestamp: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def sync_timestamp_and_recorded_at(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If timestamp is provided but recorded_at is not, set recorded_at
            if data.get("timestamp") and not data.get("recorded_at"):
                data["recorded_at"] = data["timestamp"]
            # If recorded_at is provided but timestamp is not, set timestamp
            elif data.get("recorded_at") and not data.get("timestamp"):
                data["timestamp"] = data["recorded_at"]
            # Handle location_source alias if passed
            if data.get("location_source") and not data.get("source"):
                data["source"] = data["location_source"]
        return data

class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: str
    device_id: Optional[str] = None
    latitude: float
    longitude: float
    accuracy: Optional[float] = 5.0
    source: Optional[str] = "gps"
    altitude: Optional[float] = None
    speed: Optional[float] = 0.0
    heading: Optional[float] = 0.0
    battery_level: Optional[float] = None
    address: Optional[str] = None
    recorded_at: datetime
    timestamp: Optional[datetime] = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_timestamp_field(cls, data: Any) -> Any:
        if hasattr(data, "recorded_at") and not hasattr(data, "timestamp"):
            # When reading from ORM object
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                data_dict["timestamp"] = getattr(data, "recorded_at", None)
                return data_dict
            except Exception:
                pass
        elif isinstance(data, dict) and "recorded_at" in data and "timestamp" not in data:
            data["timestamp"] = data["recorded_at"]
        return data

class CurrentLocationResponse(BaseModel):
    child_id: str
    child_name: Optional[str] = None
    current_location: Optional[LocationResponse] = None
    is_safe: bool = True
    active_zone_name: Optional[str] = None
    distance_to_caregiver_meters: Optional[float] = None
    separation_alert: bool = False
    battery_percentage: Optional[int] = None
    is_device_online: bool = True
    last_updated: Optional[datetime] = None

class LocationHistoryQuery(BaseModel):
    child_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(100, le=1000)
