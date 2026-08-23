import pytest

from app.domains.sensory.calm_strategies import get_calm_strategies
from app.domains.sensory.schemas import SensoryStateCreate


@pytest.mark.parametrize("state", [
    "too_noisy", "too_bright", "crowded", "overwhelmed",
    "need_quiet", "need_space", "need_break",
])
def test_every_supported_state_has_local_suggestions(state):
    validated = SensoryStateCreate(sensory_state=state, intensity=5)
    suggestions = get_calm_strategies(validated.sensory_state)
    assert len(suggestions) >= 2
    assert all(isinstance(item, str) and item.strip() for item in suggestions)


def test_noise_strategies_are_practical_and_supportive():
    suggestions = get_calm_strategies("too_noisy")
    assert any("quieter" in item.lower() for item in suggestions)
    assert any("headphones" in item.lower() for item in suggestions)


def test_brightness_strategies_do_not_use_medical_advice():
    combined = " ".join(get_calm_strategies("too_bright")).lower()
    assert "brightness" in combined
    assert "diagnos" not in combined
    assert "medicine" not in combined


def test_overwhelmed_strategies_include_optional_caregiver_support():
    combined = " ".join(get_calm_strategies("overwhelmed")).lower()
    assert "pause" in combined
    assert "caregiver" in combined


def test_strategy_result_is_not_shared_mutable_state():
    first = get_calm_strategies("need_break")
    first.append("changed")
    assert "changed" not in get_calm_strategies("need_break")
