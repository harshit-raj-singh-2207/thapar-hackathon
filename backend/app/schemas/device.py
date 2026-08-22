from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Any, Dict
from datetime import datetime

class DeviceCreate(BaseModel):
    child_id: Optional[str] = None
    device_name: str = Field("GPS Safety Band", example="GPS Safety Band V2")
    device_type: str = Field("gps_band", example="gps_band")
    serial_number: Optional[str] = Field(None, example="NIVARA-BAND-98231")
    device_identifier: Optional[str] = Field(None, example="NIVARA-BAND-98231")
    battery_level: Optional[int] = Field(100, ge=0, le=100)
    firmware_version: Optional[str] = "v1.2.0"

    @model_validator(mode="before")
    @classmethod
    def sync_identifiers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            ident = data.get("device_identifier") or data.get("serial_number")
            if not ident:
                raise ValueError("Either 'device_identifier' or 'serial_number' is required.")
            data["device_identifier"] = ident
            data["serial_number"] = ident
        return data

class DeviceUpdate(BaseModel):
    child_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    connection_status: Optional[str] = None
    is_online: Optional[bool] = None
    gps_status: Optional[str] = None

class DeviceHeartbeat(BaseModel):
    serial_number: str
    battery_level: int = Field(..., ge=0, le=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = 5.0
    firmware_version: Optional[str] = None

class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: Optional[str] = None
    device_name: str
    device_type: str
    serial_number: str
    device_identifier: Optional[str] = None
    battery_level: int
    is_active: bool
    is_online: bool
    connection_status: Optional[str] = "online"
    gps_status: Optional[str] = "active"
    firmware_version: Optional[str] = None
    last_ping_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_aliases(cls, data: Any) -> Any:
        if hasattr(data, "serial_number") and getattr(data, "device_identifier", None) is None:
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                data_dict["device_identifier"] = getattr(data, "serial_number")
                data_dict["last_seen"] = getattr(data, "last_seen", None) or getattr(data, "last_ping_at", None)
                data_dict["updated_at"] = getattr(data, "updated_at", None) or getattr(data, "created_at", None)
                return data_dict
            except Exception:
                pass
        return data

# Band Management Schemas
class BandCreate(BaseModel):
    device_identifier: Optional[str] = Field(None, example="BAND-LEO-001", description="Hardware unique device identifier or serial number")
    serial_number: Optional[str] = Field(None, example="BAND-LEO-001")
    device_name: Optional[str] = Field("GPS Safety Band", example="Leo's SafeBand")
    device_type: Optional[str] = Field("gps_band", example="gps_band")
    child_id: Optional[str] = Field(None, example="child-leo-1", description="Optional child ID to assign the band to")
    battery_level: Optional[int] = Field(100, ge=0, le=100, description="Initial battery percentage (0-100)")
    connection_status: Optional[str] = Field("online", example="online", description="Connection status: online, offline, standby")
    gps_status: Optional[str] = Field("active", example="active", description="GPS status: active, standby, offline, searching")
    is_online: Optional[bool] = True
    firmware_version: Optional[str] = Field("v1.2.0", example="v1.2.0")

    @model_validator(mode="before")
    @classmethod
    def sync_identifiers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            ident = data.get("device_identifier") or data.get("serial_number")
            if not ident:
                raise ValueError("Either 'device_identifier' or 'serial_number' is required.")
            data["device_identifier"] = ident
            data["serial_number"] = ident
            if "connection_status" in data and "is_online" not in data:
                data["is_online"] = data["connection_status"] in ["online", "connected"]
            elif "is_online" in data and "connection_status" not in data:
                data["connection_status"] = "online" if data["is_online"] else "offline"
        return data

class BandUpdate(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    child_id: Optional[str] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    connection_status: Optional[str] = None
    is_online: Optional[bool] = None
    gps_status: Optional[str] = None
    is_active: Optional[bool] = None
    firmware_version: Optional[str] = None

class BandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: Optional[str] = None
    device_identifier: str
    serial_number: str
    device_name: str
    device_type: str
    connection_status: str = "online"
    battery_level: int = 100
    gps_status: str = "active"
    is_active: bool = True
    is_online: bool = True
    firmware_version: Optional[str] = "v1.2.0"
    last_seen: datetime
    last_ping_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_band_aliases(cls, data: Any) -> Any:
        if hasattr(data, "serial_number"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                data_dict["device_identifier"] = getattr(data, "device_identifier", None) or getattr(data, "serial_number")
                data_dict["serial_number"] = getattr(data, "serial_number", None) or getattr(data, "device_identifier")
                data_dict["connection_status"] = getattr(data, "connection_status", "online") or ("online" if getattr(data, "is_online", True) else "offline")
                data_dict["gps_status"] = getattr(data, "gps_status", "active") or "active"
                data_dict["last_seen"] = getattr(data, "last_seen", None) or getattr(data, "last_ping_at", None) or getattr(data, "created_at", None)
                data_dict["last_ping_at"] = data_dict["last_seen"]
                data_dict["updated_at"] = getattr(data, "updated_at", None) or getattr(data, "created_at", None)
                return data_dict
            except Exception:
                pass
        return data

class BandStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    band_id: str
    device_identifier: str
    child_id: Optional[str] = None
    connection_status: str
    is_online: bool
    battery_level: int
    gps_status: str
    last_seen: datetime
    updated_at: Optional[datetime] = None

# Phone ↔ Band Connection Management Schemas
class BandPairRequest(BaseModel):
    child_id: str = Field(..., example="child-leo-1", description="Child to pair the band with")

class BandPairResponse(BaseModel):
    band_id: str
    child_id: str
    device_identifier: str
    connection_status: str = "connected"
    is_paired: bool = True
    paired_at: datetime

class BandUnpairResponse(BaseModel):
    band_id: str
    device_identifier: str
    connection_status: str = "disconnected"
    is_paired: bool = False
    unpaired_at: datetime
    message: str = "Band successfully unpaired"

class BandHeartbeatRequest(BaseModel):
    battery_level: int = Field(..., ge=0, le=100, description="Battery percentage (0-100)")
    connection_status: Optional[str] = Field("connected", description="Current connection status: connected, online, disconnected, offline")
    is_online: Optional[bool] = True
    gps_status: Optional[str] = Field("active", description="GPS status: active, standby, searching, offline")
    rssi: Optional[int] = Field(None, description="Signal strength indicator in dBm")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Optional telemetry latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Optional telemetry longitude")
    firmware_version: Optional[str] = None

class BandHeartbeatResponse(BaseModel):
    band_id: str
    device_identifier: str
    child_id: Optional[str] = None
    connection_status: str
    is_online: bool
    battery_level: int
    gps_status: str
    last_seen: datetime
    is_stale: bool = False

class BandConnectionResponse(BaseModel):
    band_id: str
    device_identifier: str
    is_paired: bool
    child_id: Optional[str] = None
    connection_status: str
    is_online: bool
    battery_level: int
    gps_status: str
    last_seen: datetime
    is_stale: bool = False
    updated_at: Optional[datetime] = None

class BandSyncRequest(BaseModel):
    sync_mode: Optional[str] = Field("full", example="full")
    client_timestamp: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

class BandSyncResponse(BaseModel):
    band_id: str
    synced: bool = True
    server_timestamp: datetime
    connection_status: str
    battery_level: int
    gps_status: str
    settings: Optional[Dict[str, Any]] = None
