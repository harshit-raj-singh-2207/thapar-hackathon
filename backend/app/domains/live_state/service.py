from datetime import datetime, timezone
from typing import Callable, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.domains.caregivers.service import get_community_caregiver_profile
from app.domains.caregivers.models import CaregiverPrivacySettings
from app.domains.communication.emotion_service import EmotionService
from app.domains.communication.service import CommunicationService
from app.domains.learning.models import Routine
from app.domains.learning.schemas import RoutineResponse
from app.domains.live_state.schemas import (
    CaregiverLiveState,
    CommunicationLiveState,
    EmotionLiveState,
    LiveStateResponse,
    LocationLiveState,
    RoutineLiveState,
    SafetyLiveState,
    SensoryLiveState,
)
from app.domains.safety.caregiver_dashboard_service import CaregiverDashboardService
from app.domains.safety.repository import LocationRepository
from app.domains.users.models import User
from app.schemas.caregiver_dashboard import ChildLocationResponse
from app.schemas.caregiver_dashboard import RecentActivityItem
from app.domains.sensory.service import SensoryStateService


class LiveStateService:
    """Read-only aggregation of the latest state held by existing domains."""

    def __init__(
        self,
        db: Session,
        *,
        emotion_service=None,
        communication_service=None,
        sensory_service=None,
        safety_service=None,
        location_repository=None,
        user_loader: Optional[Callable[[str], Optional[User]]] = None,
        routine_loader: Optional[Callable[[str], Optional[Routine]]] = None,
        caregiver_loader: Optional[Callable[[str], object]] = None,
        location_sharing_loader: Optional[Callable[[str], bool]] = None,
        now: Optional[Callable[[], datetime]] = None,
    ):
        self.db = db
        self.emotion_service = emotion_service or EmotionService(db)
        self.communication_service = communication_service or CommunicationService(db)
        self.sensory_service = sensory_service or SensoryStateService(db)
        self.safety_service = safety_service or CaregiverDashboardService(db)
        self.location_repository = location_repository or LocationRepository(db)
        self.user_loader = user_loader or self._load_user
        self.routine_loader = routine_loader or self._load_latest_routine
        self.caregiver_loader = caregiver_loader or (
            lambda user_id: get_community_caregiver_profile(self.db, user_id)
        )
        self.location_sharing_loader = (
            location_sharing_loader or self._is_location_sharing_enabled
        )
        self.now = now or (lambda: datetime.now(timezone.utc))

    def _load_user(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def _load_latest_routine(self, user_id: str) -> Optional[Routine]:
        return (
            self.db.query(Routine)
            .filter(
                Routine.is_active.is_(True),
                or_(Routine.user_id == user_id, Routine.user_id.is_(None)),
            )
            .order_by(Routine.created_at.desc())
            .first()
        )

    def _is_location_sharing_enabled(self, user_id: str) -> bool:
        settings = (
            self.db.query(CaregiverPrivacySettings)
            .filter(CaregiverPrivacySettings.user_id == user_id)
            .first()
        )
        return settings is None or settings.show_location is not False

    @staticmethod
    def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _unavailable(section_type, reason: str):
        return section_type(status="unavailable", unavailable_reason=reason)

    @staticmethod
    def _normalize_safety_state(current_status: Optional[str], active_sos: bool) -> str:
        """Map deterministic persisted safety state to the Live State vocabulary."""
        if active_sos:
            return "EMERGENCY"
        normalized = (current_status or "").strip().lower()
        if normalized == "emergency":
            return "EMERGENCY"
        if normalized in {
            "unsafe",
            "out_of_bounds",
            "separation_alert",
            "separated",
            "danger",
        }:
            return "UNSAFE"
        if normalized == "safe":
            return "SAFE"
        return "UNSURE"

    def get_user_live_state(self, user_id: str) -> LiveStateResponse:
        user = self.user_loader(user_id)
        child = user.children[0] if user and getattr(user, "children", None) else None
        child_id = child.id if child else None
        timestamps = []

        # Emotion: request one record only.
        try:
            records = self.emotion_service.get_recent_checkins(
                child_id=child_id,
                current_user=user,
                limit=1,
            )
            emotion_data = records[0] if records else None
            if emotion_data:
                emotion_updated = emotion_data.timestamp or emotion_data.created_at
                emotion = EmotionLiveState(
                    status="available", data=emotion_data, updated_at=emotion_updated
                )
                timestamps.append(emotion_updated)
            else:
                emotion = self._unavailable(EmotionLiveState, "No emotion check-in available.")
        except Exception:
            emotion = self._unavailable(EmotionLiveState, "Emotion state unavailable.")

        # Safety includes current safe/unsafe, separation and active SOS state.
        if not user or not child_id:
            safety = self._unavailable(SafetyLiveState, "No linked child available.")
        else:
            try:
                safety_data = self.safety_service.get_child_status(child_id, user)
                active_sos = safety_data.emergency_status == "active"
                recent_events = self.safety_service.get_recent_activity(
                    child_id, limit=1, current_user=user
                )
                latest_event = recent_events[0] if isinstance(recent_events, list) and recent_events else None
                if latest_event and not isinstance(latest_event, RecentActivityItem):
                    latest_event = RecentActivityItem.model_validate(latest_event)
                safety_candidates = [
                    getattr(child, "updated_at", None),
                    safety_data.last_location_update,
                    latest_event.created_at if latest_event else None,
                ]
                normalized_candidates = [
                    self._as_utc(value) for value in safety_candidates if value is not None
                ]
                safety_updated = max(normalized_candidates) if normalized_candidates else None
                safety = SafetyLiveState(
                    status="available",
                    data=safety_data,
                    state=self._normalize_safety_state(
                        safety_data.current_status, active_sos
                    ),
                    active_sos=active_sos,
                    latest_event=latest_event,
                    updated_at=safety_updated,
                )
                timestamps.append(safety_updated)
            except Exception:
                safety = self._unavailable(SafetyLiveState, "Safety state unavailable.")

        # Location: one latest location row only; no reverse-geocoding/map call.
        try:
            location_sharing_enabled = self.location_sharing_loader(user_id)
        except Exception:
            location_sharing_enabled = False

        if not location_sharing_enabled:
            location = LocationLiveState(
                status="unavailable",
                sharing_enabled=False,
                unavailable_reason="Location sharing is disabled.",
            )
        elif not child_id:
            location = LocationLiveState(
                status="unavailable",
                sharing_enabled=True,
                unavailable_reason="No linked child available.",
            )
        else:
            try:
                latest_location = self.location_repository.get_latest_location(child_id)
                if latest_location:
                    location_updated = latest_location.recorded_at or latest_location.created_at
                    location_data = ChildLocationResponse(
                        child_id=child_id,
                        latitude=latest_location.latitude,
                        longitude=latest_location.longitude,
                        accuracy=latest_location.accuracy,
                        timestamp=location_updated,
                        recorded_at=location_updated,
                        source=latest_location.source,
                        is_live=False,
                        location_available=True,
                        status="available",
                    )
                    location = LocationLiveState(
                        status="available",
                        sharing_enabled=True,
                        data=location_data,
                        updated_at=location_updated,
                    )
                    timestamps.append(location_updated)
                else:
                    location = LocationLiveState(
                        status="unavailable",
                        sharing_enabled=True,
                        unavailable_reason="No location available.",
                    )
            except Exception:
                location = LocationLiveState(
                    status="unavailable",
                    sharing_enabled=True,
                    unavailable_reason="Location state unavailable.",
                )

        # Routine: query a single newest active routine.
        try:
            latest_routine = self.routine_loader(user_id)
            if latest_routine:
                routine_data = (
                    latest_routine
                    if isinstance(latest_routine, RoutineResponse)
                    else RoutineResponse.model_validate(latest_routine, from_attributes=True)
                )
                steps = sorted(routine_data.steps, key=lambda step: step.step_number)
                completed_tasks = sum(1 for step in steps if step.is_completed)
                total_tasks = len(steps)
                current_task = next(
                    (step for step in steps if not step.is_completed), None
                )
                progress = (
                    round((completed_tasks / total_tasks) * 100, 2)
                    if total_tasks
                    else 0.0
                )
                routine_timestamps = [
                    value
                    for value in [
                        routine_data.created_at,
                        *(step.created_at for step in steps),
                    ]
                    if value is not None
                ]
                routine_updated = (
                    max(self._as_utc(value) for value in routine_timestamps)
                    if routine_timestamps
                    else None
                )
                routine = RoutineLiveState(
                    status="available",
                    data=routine_data,
                    current_task=current_task,
                    completed_tasks=completed_tasks,
                    total_tasks=total_tasks,
                    progress=progress,
                    updated_at=routine_updated,
                )
                timestamps.append(routine_updated)
            else:
                routine = self._unavailable(RoutineLiveState, "No active routine available.")
        except Exception:
            routine = self._unavailable(RoutineLiveState, "Routine state unavailable.")

        # Communication: request one non-deleted AAC/communication log only.
        try:
            logs = self.communication_service.get_recent_history(
                child_id=child_id,
                limit=1,
                current_user=user,
            )
            communication_data = logs[0] if logs else None
            if communication_data:
                communication_updated = communication_data.created_at
                communication = CommunicationLiveState(
                    status="available",
                    data=communication_data,
                    # No intent is inferred from sensitive free text. Category is
                    # exposed only when it was explicitly persisted on the log.
                    latest_intent=None,
                    message_category=communication_data.category,
                    source=communication_data.source,
                    updated_at=communication_updated,
                )
                timestamps.append(communication_updated)
            else:
                communication = self._unavailable(
                    CommunicationLiveState, "No communication available."
                )
        except Exception:
            communication = self._unavailable(
                CommunicationLiveState, "Communication state unavailable."
            )

        # Sensory: reuse the latest explicit self-report and local calm strategies.
        # This read performs no AI or external API request.
        try:
            sensory_data = self.sensory_service.get_latest_state(user_id)
            if sensory_data:
                sensory_updated = sensory_data.created_at
                sensory = SensoryLiveState(
                    status="available",
                    current_state=sensory_data.sensory_state,
                    intensity=sensory_data.intensity,
                    recommended_support=sensory_data.suggestions,
                    updated_at=sensory_updated,
                )
                timestamps.append(sensory_updated)
            else:
                sensory = self._unavailable(
                    SensoryLiveState, "No sensory state available."
                )
        except Exception:
            sensory = self._unavailable(
                SensoryLiveState, "Sensory state unavailable."
            )

        try:
            caregiver_data = self.caregiver_loader(user_id)
            caregiver_updated = None
            if caregiver_data and caregiver_data.last_seen:
                caregiver_updated = datetime.fromisoformat(caregiver_data.last_seen)
            caregiver_status = CaregiverLiveState(
                status="available", data=caregiver_data, updated_at=caregiver_updated
            )
            timestamps.append(caregiver_updated)
        except Exception:
            caregiver_status = self._unavailable(
                CaregiverLiveState, "Caregiver link unavailable."
            )

        available_timestamps = [self._as_utc(ts) for ts in timestamps if ts is not None]
        last_updated = max(available_timestamps) if available_timestamps else self.now()

        return LiveStateResponse(
            user_id=user_id,
            emotion=emotion,
            safety=safety,
            location=location,
            routine=routine,
            communication=communication,
            sensory=sensory,
            caregiver_status=caregiver_status,
            last_updated=last_updated,
        )
