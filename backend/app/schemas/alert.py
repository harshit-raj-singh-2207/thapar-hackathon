from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Any
from datetime import datetime

class CaregiverAlertResolveRequest(BaseModel):
    resolution_notes: Optional[str] = Field(None, example="Resolved by caregiver after checking child safety.")

class CaregiverAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    child_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    description: Optional[str] = None
    event_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_available: bool = False
    status: str = "unread"
    is_acknowledged: bool = False
    created_at: datetime
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_alert_fields(cls, data: Any) -> Any:
        if hasattr(data, "child_id"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                ev_type = data_dict.get("event_type") or data_dict.get("triggered_by") or "safety_alert"
                title = data_dict.get("title") or f"Safety Alert: {ev_type}"
                msg = data_dict.get("description") or data_dict.get("message") or title
                is_ack = data_dict.get("is_acknowledged", False)
                ack_at = data_dict.get("acknowledged_at")
                res_at = data_dict.get("resolved_at") or ack_at
                res_by = data_dict.get("resolved_by") or data_dict.get("acknowledged_by")

                stat = "unread"
                if hasattr(data, "status") and getattr(data, "status") in ["resolved", "active", "false_alarm"]:
                    stat = getattr(data, "status")
                elif is_ack:
                    stat = "read"

                lat = data_dict.get("latitude")
                lon = data_dict.get("longitude")

                data_dict["alert_type"] = ev_type
                data_dict["title"] = title
                data_dict["message"] = msg
                data_dict["description"] = msg
                data_dict["event_id"] = data_dict.get("id")
                data_dict["location_available"] = lat is not None and lon is not None
                data_dict["status"] = stat
                data_dict["is_acknowledged"] = is_ack
                data_dict["read_at"] = ack_at
                data_dict["acknowledged_at"] = ack_at
                data_dict["resolved_at"] = res_at
                data_dict["resolved_by"] = res_by
                return data_dict
            except Exception:
                pass
        return data
