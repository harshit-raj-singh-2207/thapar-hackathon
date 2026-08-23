from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.domains.sensory.schemas import SensoryStateCreate
from app.domains.sensory.service import SensoryStateService


def test_records_explicit_sensory_state_without_ai():
    repository = Mock()
    repository.create.side_effect = lambda record: SimpleNamespace(
        id="sensory-1", user_id=record.user_id,
        sensory_state=record.sensory_state, intensity=record.intensity,
        optional_note=record.optional_note,
        created_at=datetime(2026, 8, 23, tzinfo=timezone.utc),
    )
    service = SensoryStateService(Mock(), repository=repository)
    result = service.record_state(
        "user-1",
        SensoryStateCreate(
            sensory_state="too_noisy", intensity=8, optional_note="  cafeteria  "
        ),
    )
    assert result.user_id == "user-1"
    assert result.sensory_state == "too_noisy"
    assert result.intensity == 8
    assert result.optional_note == "cafeteria"
    repository.create.assert_called_once()


def test_latest_state_is_returned_from_repository():
    latest = SimpleNamespace(
        id="sensory-new", user_id="user-1", sensory_state="need_break",
        intensity=7, optional_note=None,
        created_at=datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc),
    )
    repository = Mock()
    repository.get_latest_for_user.return_value = latest
    result = SensoryStateService(Mock(), repository=repository).get_latest_state("user-1")
    assert result.id == "sensory-new"
    assert result.sensory_state == "need_break"
    repository.get_latest_for_user.assert_called_once_with("user-1")


def test_missing_state_returns_none():
    repository = Mock()
    repository.get_latest_for_user.return_value = None
    result = SensoryStateService(Mock(), repository=repository).get_latest_state("missing")
    assert result is None


@pytest.mark.parametrize("state", [
    "too_noisy", "too_bright", "crowded", "overwhelmed",
    "need_quiet", "need_space", "need_break",
])
def test_all_supported_states_validate(state):
    assert SensoryStateCreate(sensory_state=state, intensity=5).sensory_state == state


def test_unknown_state_is_rejected():
    with pytest.raises(ValidationError):
        SensoryStateCreate(sensory_state="unknown", intensity=5)


@pytest.mark.parametrize("intensity", [0, 11])
def test_intensity_outside_one_to_ten_is_rejected(intensity):
    with pytest.raises(ValidationError):
        SensoryStateCreate(sensory_state="overwhelmed", intensity=intensity)


def test_repository_selects_latest_state_for_user(db):
    from app.domains.sensory.models import SensoryStateRecord
    from app.domains.sensory.repository import SensoryStateRepository

    now = datetime.now(timezone.utc)
    older = SensoryStateRecord(
        user_id="user-verified-sarah", sensory_state="crowded",
        intensity=5, created_at=now - timedelta(minutes=5),
    )
    newer = SensoryStateRecord(
        user_id="user-verified-sarah", sensory_state="need_quiet",
        intensity=9, created_at=now,
    )
    other_user = SensoryStateRecord(
        user_id="user-verified-david", sensory_state="too_bright",
        intensity=4, created_at=now + timedelta(minutes=1),
    )
    db.add_all([older, newer, other_user])
    db.commit()
    result = SensoryStateRepository(db).get_latest_for_user("user-verified-sarah")
    assert result.id == newer.id
    assert result.sensory_state == "need_quiet"
