from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Tuple, Any
from datetime import datetime

class SafeZoneCreate(BaseModel):
    child_id: str = Field(..., example="child-leo-1")
    name: str = Field(..., example="Home Sanctuary", min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    center_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    center_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    radius: Optional[float] = Field(None, gt=0.0, description="Radius in meters (must be > 0)")
    radius_meters: Optional[float] = Field(None, gt=0.0)
    active: Optional[bool] = None
    is_active: Optional[bool] = True
    zone_type: Optional[str] = Field("circle", example="circle")
    polygon_coordinates: Optional[List[Tuple[float, float]]] = None
    address: Optional[str] = None
    alert_on_exit: Optional[bool] = True
    alert_on_enter: Optional[bool] = False

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            lat = data.get("latitude") if data.get("latitude") is not None else data.get("center_latitude")
            lon = data.get("longitude") if data.get("longitude") is not None else data.get("center_longitude")
            rad = data.get("radius") if data.get("radius") is not None else data.get("radius_meters")
            act = data.get("active") if data.get("active") is not None else data.get("is_active")

            if lat is None:
                raise ValueError("Latitude is required.")
            if lon is None:
                raise ValueError("Longitude is required.")
            if rad is None:
                rad = 150.0

            data["latitude"] = lat
            data["center_latitude"] = lat
            data["longitude"] = lon
            data["center_longitude"] = lon
            data["radius"] = rad
            data["radius_meters"] = rad
            data["active"] = True if act is None else bool(act)
            data["is_active"] = data["active"]
        return data

class SafeZoneUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    center_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    center_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    radius: Optional[float] = Field(None, gt=0.0)
    radius_meters: Optional[float] = Field(None, gt=0.0)
    active: Optional[bool] = None
    is_active: Optional[bool] = None
    zone_type: Optional[str] = None
    polygon_coordinates: Optional[List[Tuple[float, float]]] = None
    address: Optional[str] = None
    alert_on_exit: Optional[bool] = None
    alert_on_enter: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def sync_update_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "latitude" in data and "center_latitude" not in data:
                data["center_latitude"] = data["latitude"]
            elif "center_latitude" in data and "latitude" not in data:
                data["latitude"] = data["center_latitude"]

            if "longitude" in data and "center_longitude" not in data:
                data["center_longitude"] = data["longitude"]
            elif "center_longitude" in data and "longitude" not in data:
                data["longitude"] = data["center_longitude"]

            if "radius" in data and "radius_meters" not in data:
                data["radius_meters"] = data["radius"]
            elif "radius_meters" in data and "radius" not in data:
                data["radius"] = data["radius_meters"]

            if "active" in data and "is_active" not in data:
                data["is_active"] = data["active"]
            elif "is_active" in data and "active" not in data:
                data["active"] = data["is_active"]
        return data

class SafeZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: str
    name: str
    latitude: float
    longitude: float
    center_latitude: float
    center_longitude: float
    radius: float
    radius_meters: float
    active: bool
    is_active: bool
    zone_type: str = "circle"
    polygon_coordinates: Optional[str] = None
    address: Optional[str] = None
    alert_on_exit: bool = True
    alert_on_enter: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_response_aliases(cls, data: Any) -> Any:
        if hasattr(data, "center_latitude"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                lat = data_dict.get("center_latitude", 0.0)
                lon = data_dict.get("center_longitude", 0.0)
                rad = data_dict.get("radius_meters", 150.0)
                act = data_dict.get("is_active", True)

                data_dict["latitude"] = lat
                data_dict["center_latitude"] = lat
                data_dict["longitude"] = lon
                data_dict["center_longitude"] = lon
                data_dict["radius"] = rad
                data_dict["radius_meters"] = rad
                data_dict["active"] = act
                data_dict["is_active"] = act
                data_dict["created_at"] = getattr(data, "created_at", None) or datetime.now()
                data_dict["updated_at"] = getattr(data, "updated_at", None) or data_dict["created_at"]
                return data_dict
            except Exception:
                pass
        return data

class SafeZoneStatusCheck(BaseModel):
    child_id: str
    latitude: float
    longitude: float
    is_inside_safe_zone: bool
    is_inside: bool = True
    active_zone_id: Optional[str] = None
    active_zone_name: Optional[str] = None
    distance_to_boundary_meters: Optional[float] = None
    distance_to_center_meters: Optional[float] = None
    status: str = "safe"

    @model_validator(mode="before")
    @classmethod
    def sync_check_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            inside = data.get("is_inside_safe_zone") if data.get("is_inside_safe_zone") is not None else data.get("is_inside", True)
            data["is_inside_safe_zone"] = inside
            data["is_inside"] = inside
        return data
