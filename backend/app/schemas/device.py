from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Any, Dict
from datetime import datetime

class DeviceCreate(BaseModel):
    child_id: Optional[str] = None
    device_name: str = Field("GPS Safety Band", example="GPS Safety Band V2")
    device_type: str = Field("gps_band", example="gps_band")
    serial_number: Optional[str] = Field(None, example="NIVARA-BAND-98231")
    device_identifier: Optional[str] = Field(None, example="NIVARA-BAND-98231")
    nfc_tag_id: Optional[str] = Field(None, example="NV-NFC-001", description="Unique NFC/RFID identifier for wearable")
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
            nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
            if nfc is not None:
                data["nfc_tag_id"] = str(nfc).strip() if str(nfc).strip() else None
        return data

class DeviceUpdate(BaseModel):
    child_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    nfc_tag_id: Optional[str] = None
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
    nfc_tag_id: Optional[str] = None
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
                data_dict["nfc_tag_id"] = getattr(data, "nfc_tag_id", None)
                data_dict["last_seen"] = getattr(data, "last_seen", None) or getattr(data, "last_ping_at", None)
                data_dict["updated_at"] = getattr(data, "updated_at", None) or getattr(data, "created_at", None)
                return data_dict
            except Exception:
                pass
        return data

# Band Management Schemas
class BandCreate(BaseModel):
    band_id: Optional[str] = Field(None, example="NV-BAND-001", description="Wearable band hardware identifier or serial")
    device_identifier: Optional[str] = Field(None, example="BAND-LEO-001", description="Hardware unique device identifier or serial number")
    serial_number: Optional[str] = Field(None, example="BAND-LEO-001")
    nfc_tag_id: Optional[str] = Field(None, example="NV-NFC-001", description="Unique NFC/RFID identifier for wearable")
    device_name: Optional[str] = Field("Nivara Smart Safety Wearable", example="Leo's SafeBand")
    device_type: Optional[str] = Field("gps_band", example="gps_band")
    child_id: Optional[str] = Field(None, example="child-leo-1", description="Optional child ID to assign the band to")
    status: Optional[str] = Field("active", example="active", description="Device operating status: active, inactive, standby")
    battery_level: Optional[int] = Field(100, ge=0, le=100, description="Initial battery percentage (0-100)")
    gps_enabled: Optional[bool] = Field(True, description="Semiconductor GPS module enabled flag")
    gps_status: Optional[str] = Field("active", example="active", description="GPS status: active, standby, offline, searching")
    bluetooth_connected: Optional[bool] = Field(True, description="Semiconductor Bluetooth connection state")
    connection_status: Optional[str] = Field("online", example="online", description="Connection status: online, offline, standby, connected, disconnected")
    is_online: Optional[bool] = True
    firmware_version: Optional[str] = Field("v1.2.0", example="v1.2.0")

    @model_validator(mode="before")
    @classmethod
    def sync_identifiers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            ident = data.get("band_id") or data.get("device_identifier") or data.get("serial_number")
            if not ident:
                # If nfc_tag_id is supplied without serial number, derive or set serial identifier
                nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
                if nfc:
                    ident = f"BAND-{nfc}"
                else:
                    raise ValueError("Either 'band_id', 'device_identifier' or 'serial_number' is required.")
            data["band_id"] = ident
            data["device_identifier"] = ident
            data["serial_number"] = ident
            nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
            if nfc is not None:
                data["nfc_tag_id"] = str(nfc).strip() if str(nfc).strip() else None
            
            # Sync semiconductor / connectivity fields
            if "connection_status" in data and "is_online" not in data:
                data["is_online"] = data["connection_status"] in ["online", "connected"]
            elif "is_online" in data and "connection_status" not in data:
                data["connection_status"] = "online" if data["is_online"] else "offline"
            
            if "bluetooth_connected" not in data:
                data["bluetooth_connected"] = data.get("connection_status") in ["online", "connected"]
            if "gps_enabled" not in data:
                data["gps_enabled"] = data.get("gps_status") not in ["offline", "disabled"]
        return data

class BandUpdate(BaseModel):
    band_id: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    child_id: Optional[str] = None
    nfc_tag_id: Optional[str] = None
    status: Optional[str] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    gps_enabled: Optional[bool] = None
    gps_status: Optional[str] = None
    bluetooth_connected: Optional[bool] = None
    connection_status: Optional[str] = None
    is_online: Optional[bool] = None
    is_active: Optional[bool] = None
    firmware_version: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_nfc_update(cls, data: Any) -> Any:
        if isinstance(data, dict):
            nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
            if nfc is not None:
                data["nfc_tag_id"] = str(nfc).strip() if str(nfc).strip() else None
        return data

class BandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    band_id: str
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    child: Optional[Dict[str, Any]] = None
    device_identifier: str
    serial_number: str
    nfc_tag_id: Optional[str] = None
    status: str = "active"
    device_status: str = "active"
    battery_level: int = 100
    battery: int = 100
    gps_enabled: bool = True
    gps_status: str = "active"
    bluetooth_connected: bool = True
    bluetooth_status: str = "connected"
    connection_status: str = "online"
    device_name: str = "GPS Safety Band"
    device_type: str = "gps_band"
    is_active: bool = True
    is_online: bool = True
    firmware_version: Optional[str] = "v1.2.0"
    last_seen: datetime
    last_seen_at: datetime
    last_ping_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_band_aliases(cls, data: Any) -> Any:
        if hasattr(data, "serial_number") or hasattr(data, "id"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                ident = getattr(data, "device_identifier", None) or getattr(data, "serial_number", None) or getattr(data, "id")
                data_dict["band_id"] = ident
                data_dict["device_identifier"] = ident
                data_dict["serial_number"] = getattr(data, "serial_number", None) or ident
                data_dict["nfc_tag_id"] = getattr(data, "nfc_tag_id", None)
                data_dict["status"] = getattr(data, "status", None) or ("active" if getattr(data, "is_active", True) else "inactive")
                data_dict["device_status"] = data_dict["status"]
                data_dict["battery"] = getattr(data, "battery_level", 100)
                data_dict["battery_level"] = data_dict["battery"]
                data_dict["gps_enabled"] = getattr(data, "gps_enabled", True) if getattr(data, "gps_enabled", None) is not None else (getattr(data, "gps_status", "active") != "offline")
                data_dict["gps_status"] = getattr(data, "gps_status", "active") or "active"
                data_dict["bluetooth_connected"] = getattr(data, "bluetooth_connected", True) if getattr(data, "bluetooth_connected", None) is not None else (getattr(data, "connection_status", "online") in ["online", "connected"])
                data_dict["bluetooth_status"] = "connected" if data_dict["bluetooth_connected"] else "disconnected"
                data_dict["connection_status"] = getattr(data, "connection_status", "online") or ("online" if getattr(data, "is_online", True) else "offline")
                
                last_time = getattr(data, "last_seen_at", None) or getattr(data, "last_seen", None) or getattr(data, "last_ping_at", None) or getattr(data, "created_at", None)
                data_dict["last_seen"] = last_time
                data_dict["last_seen_at"] = last_time
                data_dict["last_ping_at"] = last_time
                data_dict["updated_at"] = getattr(data, "updated_at", None) or getattr(data, "created_at", None)
                
                if hasattr(data, "child") and data.child:
                    data_dict["child_name"] = data.child.name
                    data_dict["child"] = {
                        "id": data.child.id,
                        "name": data.child.name,
                        "age": data.child.age,
                        "caregiver_id": data.child.caregiver_id,
                    }
                return data_dict
            except Exception:
                pass
        return data

class BandStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    band_id: str
    device_identifier: str
    nfc_tag_id: Optional[str] = None
    child_id: Optional[str] = None
    status: Optional[str] = "active"
    device_status: Optional[str] = "active"
    connection_status: str
    is_online: bool
    battery_level: int
    battery: Optional[int] = 100
    gps_enabled: Optional[bool] = True
    gps_status: str
    bluetooth_connected: Optional[bool] = True
    bluetooth_status: Optional[str] = "connected"
    last_seen: datetime
    last_seen_at: Optional[datetime] = None
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
    gps_enabled: Optional[bool] = Field(True, description="Semiconductor GPS module enabled")
    gps_status: Optional[str] = Field("active", description="GPS status: active, standby, searching, offline")
    bluetooth_connected: Optional[bool] = Field(True, description="Semiconductor BLE status")
    status: Optional[str] = Field("active", description="Device status")
    rssi: Optional[int] = Field(None, description="Signal strength indicator in dBm")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Optional telemetry latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Optional telemetry longitude")
    firmware_version: Optional[str] = None

class BandHeartbeatResponse(BaseModel):
    band_id: str
    device_identifier: str
    child_id: Optional[str] = None
    status: Optional[str] = "active"
    connection_status: str
    is_online: bool
    battery_level: int
    gps_enabled: Optional[bool] = True
    gps_status: str
    bluetooth_connected: Optional[bool] = True
    last_seen: datetime
    last_seen_at: Optional[datetime] = None
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

# ==========================================
# RFID / NFC Wearable Identity Schemas
# ==========================================

class NFCWearableRegisterRequest(BaseModel):
    nfc_tag_id: str = Field(..., example="NV-NFC-001", description="Unique NFC/RFID tag identifier (e.g., NV-NFC-001)")
    band_id: Optional[str] = Field(None, example="NV-BAND-001", description="Wearable band hardware identifier or serial")
    serial_number: Optional[str] = Field(None, example="NV-BAND-001")
    device_identifier: Optional[str] = Field(None, example="NV-BAND-001")
    child_id: Optional[str] = Field(None, example="child-leo-1", description="Optional child ID to assign the NFC wearable to")
    device_name: Optional[str] = Field("Nivara NFC Wearable Band", example="Leo's SafeBand")
    device_type: Optional[str] = Field("nfc_wearable", example="nfc_wearable")
    battery_level: Optional[int] = Field(100, ge=0, le=100)
    gps_enabled: Optional[bool] = True
    gps_status: Optional[str] = Field("active", example="active")
    bluetooth_connected: Optional[bool] = True
    connection_status: Optional[str] = Field("online", example="online")
    firmware_version: Optional[str] = Field("v1.2.0", example="v1.2.0")

    @model_validator(mode="before")
    @classmethod
    def sync_nfc_payload(cls, data: Any) -> Any:
        if isinstance(data, dict):
            nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
            if not nfc or not str(nfc).strip():
                raise ValueError("nfc_tag_id is required and cannot be empty.")
            data["nfc_tag_id"] = str(nfc).strip()
            ident = data.get("band_id") or data.get("device_identifier") or data.get("serial_number")
            if not ident:
                ident = f"BAND-{data['nfc_tag_id']}"
            data["band_id"] = ident
            data["device_identifier"] = ident
            data["serial_number"] = ident
        return data

class NFCWearableUpdateRequest(BaseModel):
    nfc_tag_id: str = Field(..., example="NV-NFC-002", description="New unique NFC/RFID tag identifier")

    @model_validator(mode="before")
    @classmethod
    def validate_nfc(cls, data: Any) -> Any:
        if isinstance(data, dict):
            nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
            if not nfc or not str(nfc).strip():
                raise ValueError("nfc_tag_id is required and cannot be empty.")
            data["nfc_tag_id"] = str(nfc).strip()
        return data

class NFCVerifyRequest(BaseModel):
    nfc_tag_id: str = Field(..., example="NV-NFC-001", description="NFC/RFID identifier to verify")

    @model_validator(mode="before")
    @classmethod
    def validate_nfc(cls, data: Any) -> Any:
        if isinstance(data, dict):
            nfc = data.get("nfc_tag_id") or data.get("nfc_id") or data.get("rfid_id")
            if not nfc or not str(nfc).strip():
                raise ValueError("nfc_tag_id is required and cannot be empty.")
            data["nfc_tag_id"] = str(nfc).strip()
        return data

class NFCVerifyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    verified: bool = True
    is_valid: bool = True
    nfc_tag_id: Optional[str] = None
    band_id: Optional[str] = None
    device_identifier: Optional[str] = None
    device_name: Optional[str] = None
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    caregiver_id: Optional[str] = None
    status: Optional[str] = "active"
    reason: Optional[str] = None
    is_active: bool = True
    battery_level: Optional[int] = 100
    gps_enabled: Optional[bool] = True
    bluetooth_connected: Optional[bool] = True
    last_seen_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

class NFCWearableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    band_id: str
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    nfc_tag_id: str
    status: str = "active"
    device_name: str
    device_type: str = "nfc_wearable"
    battery_level: int = 100
    gps_enabled: bool = True
    bluetooth_connected: bool = True
    connection_status: str = "online"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_wearable_aliases(cls, data: Any) -> Any:
        if hasattr(data, "id"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                data_dict["band_id"] = getattr(data, "id")
                data_dict["status"] = getattr(data, "status", None) or ("active" if getattr(data, "is_active", True) else "inactive")
                if hasattr(data, "child") and data.child:
                    data_dict["child_name"] = data.child.name
                data_dict["updated_at"] = getattr(data, "updated_at", None) or getattr(data, "created_at", None)
                return data_dict
            except Exception:
                pass
        return data

