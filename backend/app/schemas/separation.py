from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class SeparationEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_id: str
    child_name: str
    is_separated: bool
    separation_reason: Optional[str] = None  # band_disconnected, heartbeat_timeout, distance_exceeded, None
    severity: str = "normal"  # normal, warning, critical
    distance_meters: Optional[float] = None
    threshold_meters: float
    heartbeat_timeout_seconds: int
    time_since_last_heartbeat_seconds: Optional[float] = None
    is_band_connected: bool
    last_known_location: Optional[Dict[str, Any]] = None
    active_event_id: Optional[str] = None
    alert_created: bool = False

class SeparationStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_id: str
    child_name: str
    is_separated: bool
    separation_reason: Optional[str] = None
    current_status: str
    distance_meters: Optional[float] = None
    threshold_meters: float
    is_band_connected: bool
    last_known_location: Optional[Dict[str, Any]] = None
    has_active_alert: bool

class SeparationResolveResponse(BaseModel):
    child_id: str
    resolved: bool = True
    resolved_events_count: int
    current_status: str = "safe"
    message: str = "Separation event resolved and child status restored to safe."
    resolved_at: datetime
