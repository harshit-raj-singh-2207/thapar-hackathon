from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# ==============================================================================
# Preferences Schemas
# ==============================================================================

class EmergencySupportPreferencesBase(BaseModel):
    communication_enabled: bool = Field(True, description="Enable remote AAC & AI communication")
    learning_enabled: bool = Field(True, description="Enable remote routines & AI tutor")
    emotional_support_enabled: bool = Field(True, description="Enable emotion tracking & sensory tools")
    games_enabled: bool = Field(True, description="Enable indoor educational & cognitive games")
    safety_monitoring_enabled: bool = Field(True, description="Enable continuous GPS & telemetry")
    caregiver_notifications_enabled: bool = Field(True, description="Enable instant remote alert cascades")


class EmergencySupportPreferencesUpdate(BaseModel):
    communication_enabled: Optional[bool] = None
    learning_enabled: Optional[bool] = None
    emotional_support_enabled: Optional[bool] = None
    games_enabled: Optional[bool] = None
    safety_monitoring_enabled: Optional[bool] = None
    caregiver_notifications_enabled: Optional[bool] = None


class EmergencySupportPreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    emergency_mode_id: str
    communication_enabled: bool
    learning_enabled: bool
    emotional_support_enabled: bool
    games_enabled: bool
    safety_monitoring_enabled: bool
    caregiver_notifications_enabled: bool
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Emergency Mode CRUD Schemas
# ==============================================================================

class EmergencyModeCreate(BaseModel):
    child_id: str = Field(..., example="child-leo-1", description="Target child ID")
    status: Optional[str] = Field("active", example="active", description="scheduled, active, expired, inactive")
    emergency_type: Optional[str] = Field("pandemic_lockdown", example="pandemic_lockdown")
    duration_days: Optional[int] = Field(90, ge=1, le=365, example=90, description="Duration in days")
    start_date: Optional[datetime] = Field(None, description="Optional start datetime, defaults to UTC now")
    end_date: Optional[datetime] = Field(None, description="Optional end datetime, defaults to start_date + duration_days")
    reason: Optional[str] = Field(
        "Worldwide Pandemic Emergency - Physical Gathering Restrictions",
        example="Worldwide Pandemic Emergency - Physical Gathering Restrictions",
        description="Reason/context for emergency mode",
    )
    preferences: Optional[EmergencySupportPreferencesBase] = None


class EmergencyModeUpdate(BaseModel):
    status: Optional[str] = Field(None, example="active", description="scheduled, active, expired, inactive")
    emergency_type: Optional[str] = Field(None, description="Updated emergency category")
    is_active: Optional[bool] = Field(None, description="Toggle active status of emergency mode")
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="Updated duration in days")
    start_date: Optional[datetime] = Field(None, description="Updated start datetime")
    end_date: Optional[datetime] = Field(None, description="Updated end datetime")
    reason: Optional[str] = Field(None, description="Updated emergency reason")
    preferences: Optional[EmergencySupportPreferencesUpdate] = Field(None, description="Updated support preferences")


class EmergencyModeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    child_id: str
    caregiver_id: str
    status: str = "active"
    emergency_type: str = "pandemic_lockdown"
    is_active: bool
    is_expired: bool
    effective_status: str = "active"
    start_date: datetime
    end_date: datetime
    duration_days: int
    days_remaining: int
    reason: str
    preferences: EmergencySupportPreferencesResponse
    created_at: datetime
    updated_at: datetime



# ==============================================================================
# Emergency Dashboard Summary Schemas
# ==============================================================================

class SupportModuleStatus(BaseModel):
    status: str  # ACTIVE, DISABLED, STANDBY
    enabled: bool
    available_tools: List[str]
    details: Optional[Dict[str, Any]] = None


class EmergencyDashboardSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    child_id: str
    child_name: str
    age: Optional[int] = None
    autism_level: Optional[str] = None
    avatar_url: Optional[str] = None
    current_status: str

    emergency_mode: Optional[EmergencyModeResponse] = None
    is_emergency_mode_active: bool

    communication_support: SupportModuleStatus
    learning_support: SupportModuleStatus
    emotional_support: SupportModuleStatus
    games_support: Optional[SupportModuleStatus] = None
    safety_support: SupportModuleStatus
    gps_status: Optional[SupportModuleStatus] = None
    nfc_device_status: Optional[SupportModuleStatus] = None
    sos_emergency_status: Optional[SupportModuleStatus] = None
    caregiver_coordination: SupportModuleStatus


# ==============================================================================
# NFC Safe Emergency Identification Card Schema
# ==============================================================================

class NFCEmergencyCardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nfc_tag_id: str
    band_id: Optional[str] = None
    child_id: Optional[str] = None
    child_display_name: Optional[str] = None
    is_emergency_mode_active: bool = False
    emergency_status: str = "normal"
    caregiver_name: Optional[str] = None
    caregiver_phone: Optional[str] = None
    emergency_contacts: List[Dict[str, Any]] = Field(default_factory=list)
    safety_instructions: str = "Child is autistic and may be non-verbal. Please speak gently and calmly. Do not crowd. Contact the primary guardian immediately."
    scanned_at: datetime


