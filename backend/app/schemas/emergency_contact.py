from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from typing import Optional, Any
from datetime import datetime
import re

PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)\.]{7,20}$")

class EmergencyContactCreate(BaseModel):
    child_id: Optional[str] = Field(None, example="child-leo-1")
    name: str = Field(..., example="Dr. Emily Watson", min_length=1)
    relationship: Optional[str] = Field(None, example="Mother")
    relationship_type: Optional[str] = Field(None, example="Mother")
    phone: Optional[str] = Field(None, example="+1-555-0199")
    phone_number: Optional[str] = Field(None, example="+1-555-0199")
    email: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1)
    priority_order: Optional[int] = Field(None, ge=1)
    active: Optional[bool] = True
    is_active: Optional[bool] = True
    notify_via_sms: bool = True
    notify_via_call: bool = True
    notify_via_push: bool = True

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Name check
            name = data.get("name")
            if not name or not str(name).strip():
                raise ValueError("Contact name is required and cannot be empty.")

            # Relationship alias
            rel = data.get("relationship") or data.get("relationship_type") or "Family"
            if not str(rel).strip():
                raise ValueError("Relationship cannot be empty.")
            data["relationship"] = str(rel).strip()
            data["relationship_type"] = str(rel).strip()

            # Phone alias
            ph = data.get("phone") or data.get("phone_number")
            if not ph or not str(ph).strip():
                raise ValueError("Phone number is required.")
            ph_str = str(ph).strip()
            if not PHONE_REGEX.match(ph_str):
                raise ValueError(f"Invalid phone number format: '{ph_str}'.")
            data["phone"] = ph_str
            data["phone_number"] = ph_str

            # Priority alias
            prio = data.get("priority") if data.get("priority") is not None else data.get("priority_order")
            if prio is not None and prio < 1:
                raise ValueError("Priority must be 1 or greater.")
            prio_val = prio if prio is not None else 1
            data["priority"] = prio_val
            data["priority_order"] = prio_val

            # Active alias
            act = data.get("active") if data.get("active") is not None else data.get("is_active")
            act_val = True if act is None else bool(act)
            data["active"] = act_val
            data["is_active"] = act_val
        return data

class EmergencyContactUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    relationship_type: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1)
    priority_order: Optional[int] = Field(None, ge=1)
    active: Optional[bool] = None
    is_active: Optional[bool] = None
    notify_via_sms: Optional[bool] = None
    notify_via_call: Optional[bool] = None
    notify_via_push: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def sync_update_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" in data and data["name"] is not None:
                if not str(data["name"]).strip():
                    raise ValueError("Name cannot be empty.")
            rel = data.get("relationship") or data.get("relationship_type")
            if rel is not None:
                if not str(rel).strip():
                    raise ValueError("Relationship cannot be empty.")
                data["relationship"] = str(rel).strip()
                data["relationship_type"] = str(rel).strip()
            ph = data.get("phone") or data.get("phone_number")
            if ph is not None:
                ph_str = str(ph).strip()
                if not PHONE_REGEX.match(ph_str):
                    raise ValueError(f"Invalid phone number format: '{ph_str}'.")
                data["phone"] = ph_str
                data["phone_number"] = ph_str
            prio = data.get("priority") if data.get("priority") is not None else data.get("priority_order")
            if prio is not None:
                if prio < 1:
                    raise ValueError("Priority must be 1 or greater.")
                data["priority"] = prio
                data["priority_order"] = prio
            act = data.get("active") if data.get("active") is not None else data.get("is_active")
            if act is not None:
                data["active"] = bool(act)
                data["is_active"] = bool(act)
        return data

class EmergencyContactStatusUpdate(BaseModel):
    active: Optional[bool] = None
    is_active: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def sync_status(cls, data: Any) -> Any:
        if isinstance(data, dict):
            act = data.get("active") if data.get("active") is not None else data.get("is_active")
            act_val = True if act is None else bool(act)
            data["active"] = act_val
            data["is_active"] = act_val
        return data

class EmergencyContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: Optional[str] = None
    child_id: Optional[str] = None
    name: str
    phone: str
    phone_number: str
    relationship: str
    relationship_type: str
    priority: int
    priority_order: int
    active: bool = True
    is_active: bool = True
    email: Optional[str] = None
    notify_via_sms: bool = True
    notify_via_call: bool = True
    notify_via_push: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def populate_contact_aliases(cls, data: Any) -> Any:
        if hasattr(data, "name"):
            try:
                data_dict = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                ph = data_dict.get("phone_number") or data_dict.get("phone") or ""
                rel = data_dict.get("relationship_type") or data_dict.get("relationship") or "Family"
                prio = data_dict.get("priority_order") or data_dict.get("priority") or 1
                act = data_dict.get("is_active") if data_dict.get("is_active") is not None else True

                data_dict["phone"] = ph
                data_dict["phone_number"] = ph
                data_dict["relationship"] = rel
                data_dict["relationship_type"] = rel
                data_dict["priority"] = prio
                data_dict["priority_order"] = prio
                data_dict["active"] = act
                data_dict["is_active"] = act
                data_dict["updated_at"] = data_dict.get("updated_at") or data_dict.get("created_at")
                return data_dict
            except Exception:
                pass
        return data
