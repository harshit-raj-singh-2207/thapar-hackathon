from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from app.domains.caregivers.schemas import CommunityCaregiverProfileSchema
from app.domains.communication.schemas import (
    CommunicationLogResponse,
    EmotionCheckinResponse,
)
from app.domains.learning.schemas import RoutineResponse, RoutineStepResponse
from app.domains.live_state.service import LiveStateService
from app.schemas.caregiver_dashboard import ChildStatusResponse
from app.schemas.caregiver_dashboard import RecentActivityItem


def _dependencies(now):
    child = SimpleNamespace(id="child-1", updated_at=now - timedelta(minutes=2))
    user = SimpleNamespace(id="user-1", children=[child])

    emotion = Mock()
    emotion.get_recent_checkins.return_value = [
        EmotionCheckinResponse(
            id="emotion-1",
            child_id=child.id,
            user_id=user.id,
            emotion="calm",
            intensity=4,
            created_at=now - timedelta(minutes=5),
            timestamp=now - timedelta(minutes=5),
        )
    ]

    communication = Mock()
    communication.get_recent_history.return_value = [
        CommunicationLogResponse(
            id="log-1",
            child_id=child.id,
            user_id=user.id,
            sentence="I need water.",
            source="aac",
            audio_played=True,
            created_at=now - timedelta(minutes=1),
        )
    ]

    safety = Mock()
    safety.get_child_status.return_value = ChildStatusResponse(
        child_id=child.id,
        name="Sam",
        current_status="safe",
        last_location_update=now - timedelta(minutes=3),
    )
    safety.get_recent_activity.return_value = []

    location = Mock()
    location.get_latest_location.return_value = SimpleNamespace(
        latitude=30.1,
        longitude=76.2,
        accuracy=4.0,
        source="gps",
        recorded_at=now - timedelta(minutes=3),
        created_at=now - timedelta(minutes=3),
    )

    routine = RoutineResponse(
        id="routine-1",
        title="Morning routine",
        steps=[],
        created_at=now - timedelta(hours=1),
    )
    caregiver = CommunityCaregiverProfileSchema(
        id="caregiver-1",
        user_id=user.id,
        name="Parent",
        is_verified=True,
        is_online=True,
        last_seen=(now - timedelta(minutes=4)).isoformat(),
    )
    return user, emotion, communication, safety, location, routine, caregiver


def test_live_state_collects_only_latest_records_and_calculates_last_updated():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    routine_loader = Mock(return_value=routine)
    caregiver_loader = Mock(return_value=caregiver)

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=routine_loader,
        caregiver_loader=caregiver_loader,
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.emotion.data.emotion == "calm"
    assert result.safety.data.current_status == "safe"
    assert result.safety.state == "SAFE"
    assert result.safety.active_sos is False
    assert result.location.data.latitude == 30.1
    assert result.location.sharing_enabled is True
    assert result.location.data.longitude == 76.2
    assert result.location.data.accuracy == 4.0
    assert result.location.updated_at == now - timedelta(minutes=3)
    assert result.routine.data.id == "routine-1"
    assert result.communication.data.sentence == "I need water."
    assert result.caregiver_status.data.id == "caregiver-1"
    assert result.last_updated == now - timedelta(minutes=1)
    emotion.get_recent_checkins.assert_called_once_with(
        child_id="child-1", current_user=user, limit=1
    )
    communication.get_recent_history.assert_called_once_with(
        child_id="child-1", limit=1, current_user=user
    )
    location.get_latest_location.assert_called_once_with("child-1")
    routine_loader.assert_called_once_with("user-1")


def test_live_state_marks_missing_subsystems_unavailable():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user = SimpleNamespace(id="user-1", children=[])
    emotion = Mock()
    emotion.get_recent_checkins.return_value = []
    communication = Mock()
    communication.get_recent_history.return_value = []
    safety = Mock()
    location = Mock()

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=None),
        caregiver_loader=Mock(side_effect=LookupError),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.emotion.status == "unavailable"
    assert result.safety.status == "unavailable"
    assert result.location.status == "unavailable"
    assert result.location.sharing_enabled is True
    assert result.routine.status == "unavailable"
    assert result.communication.status == "unavailable"
    assert result.caregiver_status.status == "unavailable"
    assert result.last_updated == now
    safety.get_child_status.assert_not_called()
    location.get_latest_location.assert_not_called()


def test_location_sharing_enabled_with_no_location_is_cleanly_unavailable():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    location.get_latest_location.return_value = None

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.location.sharing_enabled is True
    assert result.location.status == "unavailable"
    assert result.location.data is None
    assert result.location.updated_at is None
    location.get_latest_location.assert_called_once_with("child-1")


def test_live_state_uses_coordinate_returned_by_latest_location_lookup():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    latest_time = now - timedelta(seconds=10)
    location.get_latest_location.return_value = SimpleNamespace(
        latitude=31.999,
        longitude=77.888,
        accuracy=2.5,
        source="gps",
        recorded_at=latest_time,
        created_at=now - timedelta(minutes=10),
    )

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.location.data.latitude == 31.999
    assert result.location.data.longitude == 77.888
    assert result.location.data.accuracy == 2.5
    assert result.location.updated_at == latest_time
    location.get_latest_location.assert_called_once_with("child-1")


def test_one_subsystem_failure_does_not_fail_live_state():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    emotion.get_recent_checkins.side_effect = RuntimeError("database unavailable")

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.emotion.status == "unavailable"
    assert result.communication.status == "available"
    assert result.safety.status == "available"


def test_location_sharing_disabled_does_not_fetch_or_expose_location():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=False),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.location.status == "unavailable"
    assert result.location.sharing_enabled is False
    assert result.location.data is None
    assert result.location.unavailable_reason == "Location sharing is disabled."
    location.get_latest_location.assert_not_called()


def test_live_state_returns_latest_emotion_intensity_and_timestamp():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.emotion.data.emotion == "calm"
    assert result.emotion.data.intensity == 4
    assert result.emotion.updated_at == now - timedelta(minutes=5)
    emotion.get_recent_checkins.assert_called_once_with(
        child_id="child-1", current_user=user, limit=1
    )


def test_deterministic_unsafe_state_includes_latest_safety_event():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    event_time = now - timedelta(seconds=30)
    safety.get_child_status.return_value = ChildStatusResponse(
        child_id="child-1",
        name="Sam",
        current_status="out_of_bounds",
        emergency_status="none",
    )
    safety.get_recent_activity.return_value = [
        RecentActivityItem(
            id="event-1",
            child_id="child-1",
            event_type="geofence_exit",
            severity="critical",
            title="Left safe zone",
            created_at=event_time,
        )
    ]

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.safety.state == "UNSAFE"
    assert result.safety.active_sos is False
    assert result.safety.latest_event.id == "event-1"
    assert result.safety.updated_at == event_time
    safety.get_recent_activity.assert_called_once_with(
        "child-1", limit=1, current_user=user
    )


def test_active_sos_deterministically_overrides_safety_state_to_emergency():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    safety.get_child_status.return_value = ChildStatusResponse(
        child_id="child-1",
        name="Sam",
        current_status="safe",
        emergency_status="active",
        active_emergency_id="emergency-1",
    )

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.safety.state == "EMERGENCY"
    assert result.safety.active_sos is True
    assert result.safety.data.active_emergency_id == "emergency-1"


def test_live_state_calculates_current_routine_progress_from_existing_steps():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, _, caregiver = _dependencies(now)
    routine = RoutineResponse(
        id="routine-1",
        title="Morning routine",
        created_at=now - timedelta(hours=1),
        steps=[
            RoutineStepResponse(
                id="step-1",
                routine_id="routine-1",
                step_number=1,
                title="Wake up",
                is_completed=True,
                created_at=now - timedelta(minutes=50),
            ),
            RoutineStepResponse(
                id="step-2",
                routine_id="routine-1",
                step_number=2,
                title="Brush teeth",
                is_completed=False,
                created_at=now - timedelta(minutes=45),
            ),
            RoutineStepResponse(
                id="step-3",
                routine_id="routine-1",
                step_number=3,
                title="Get dressed",
                is_completed=False,
                created_at=now - timedelta(minutes=40),
            ),
        ],
    )

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.routine.total_tasks == 3
    assert result.routine.completed_tasks == 1
    assert result.routine.progress == 33.33
    assert result.routine.current_task.id == "step-2"
    assert result.routine.updated_at == now - timedelta(minutes=40)


def test_live_state_returns_only_stored_latest_communication_metadata():
    now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
    user, emotion, communication, safety, location, routine, caregiver = _dependencies(now)
    communication.get_recent_history.return_value = [
        CommunicationLogResponse(
            id="log-latest",
            child_id="child-1",
            user_id="user-1",
            sentence="Please explain this.",
            source="ai_sentence",
            category="learning_help",
            audio_played=False,
            created_at=now - timedelta(seconds=20),
        )
    ]

    result = LiveStateService(
        Mock(),
        emotion_service=emotion,
        communication_service=communication,
        safety_service=safety,
        location_repository=location,
        user_loader=Mock(return_value=user),
        routine_loader=Mock(return_value=routine),
        caregiver_loader=Mock(return_value=caregiver),
        location_sharing_loader=Mock(return_value=True),
        now=lambda: now,
    ).get_user_live_state(user.id)

    assert result.communication.latest_intent is None
    assert result.communication.message_category == "learning_help"
    assert result.communication.source == "ai_sentence"
    assert result.communication.updated_at == now - timedelta(seconds=20)
    communication.get_recent_history.assert_called_once_with(
        child_id="child-1", limit=1, current_user=user
    )
