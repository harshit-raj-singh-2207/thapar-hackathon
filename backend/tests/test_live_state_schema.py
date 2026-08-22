from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.domains.live_state.schemas import LiveStateResponse


def test_live_state_supports_clean_unavailable_sections():
    now = datetime.now(timezone.utc)

    state = LiveStateResponse(user_id="user-1", last_updated=now)

    assert state.user_id == "user-1"
    assert state.last_updated == now
    assert state.emotion.status == "unavailable"
    assert state.emotion.data is None
    assert state.location.updated_at is None
    assert state.caregiver_status.data is None


def test_live_state_accepts_existing_domain_response_shapes():
    now = datetime.now(timezone.utc)
    state = LiveStateResponse(
        user_id="user-1",
        emotion={
            "status": "available",
            "updated_at": now,
            "data": {
                "id": "emotion-1",
                "user_id": "user-1",
                "emotion": "calm",
                "intensity": 4,
                "created_at": now,
            },
        },
        communication={
            "status": "available",
            "updated_at": now,
            "data": {
                "id": "log-1",
                "user_id": "user-1",
                "sentence": "I need a break.",
                "source": "aac",
                "audio_played": True,
                "created_at": now,
            },
        },
        last_updated=now,
    )

    assert state.emotion.data.emotion == "calm"
    assert state.communication.data.sentence == "I need a break."
    assert state.safety.status == "unavailable"


def test_live_state_rejects_unknown_availability_status():
    with pytest.raises(ValidationError):
        LiveStateResponse(
            user_id="user-1",
            emotion={"status": "missing"},
            last_updated=datetime.now(timezone.utc),
        )
