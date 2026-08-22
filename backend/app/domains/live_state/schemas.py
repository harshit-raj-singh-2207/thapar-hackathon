from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domains.caregivers.schemas import CommunityCaregiverProfileSchema
from app.domains.communication.schemas import (
    CommunicationLogResponse,
    EmotionCheckinResponse,
)
from app.domains.learning.schemas import RoutineResponse, RoutineStepResponse
from app.schemas.caregiver_dashboard import (
    ChildLocationResponse,
    ChildStatusResponse,
    RecentActivityItem,
)


LiveStateAvailability = Literal["available", "unavailable"]


class LiveStateSection(BaseModel):
    """Availability metadata shared by every aggregated state section."""

    model_config = ConfigDict(extra="forbid")

    status: LiveStateAvailability = "unavailable"
    updated_at: Optional[datetime] = None
    unavailable_reason: Optional[str] = None


class EmotionLiveState(LiveStateSection):
    data: Optional[EmotionCheckinResponse] = None


class SafetyLiveState(LiveStateSection):
    data: Optional[ChildStatusResponse] = None
    state: Optional[Literal["SAFE", "UNSURE", "UNSAFE", "EMERGENCY"]] = None
    active_sos: bool = False
    latest_event: Optional[RecentActivityItem] = None


class LocationLiveState(LiveStateSection):
    sharing_enabled: bool = False
    data: Optional[ChildLocationResponse] = None


class RoutineLiveState(LiveStateSection):
    data: Optional[RoutineResponse] = None
    current_task: Optional[RoutineStepResponse] = None
    completed_tasks: int = Field(default=0, ge=0)
    total_tasks: int = Field(default=0, ge=0)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)


class CommunicationLiveState(LiveStateSection):
    data: Optional[CommunicationLogResponse] = None
    latest_intent: Optional[str] = None
    message_category: Optional[str] = None
    source: Optional[str] = None


class CaregiverLiveState(LiveStateSection):
    data: Optional[CommunityCaregiverProfileSchema] = None


class LiveStateResponse(BaseModel):
    """Current cross-domain state assembled from existing NIVARA records."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    emotion: EmotionLiveState = Field(default_factory=EmotionLiveState)
    safety: SafetyLiveState = Field(default_factory=SafetyLiveState)
    location: LocationLiveState = Field(default_factory=LocationLiveState)
    routine: RoutineLiveState = Field(default_factory=RoutineLiveState)
    communication: CommunicationLiveState = Field(default_factory=CommunicationLiveState)
    caregiver_status: CaregiverLiveState = Field(default_factory=CaregiverLiveState)
    last_updated: datetime
