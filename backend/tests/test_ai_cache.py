import pytest

from app.ai import cache as cache_module
from app.ai.cache import TTLCache, build_cache_key


def test_cache_hit_returns_independent_value_copy():
    cache = TTLCache(ttl_seconds=60)
    cache.set("answer", {"text": "Use short words."})
    result = cache.get("answer")
    assert result == {"text": "Use short words."}
    result["text"] = "changed"
    assert cache.get("answer") == {"text": "Use short words."}


def test_cache_miss_and_delete():
    cache = TTLCache(ttl_seconds=60)
    assert cache.get("missing") is None
    cache.set("temporary", "value")
    assert cache.delete("temporary") is True
    assert cache.get("temporary") is None
    assert cache.delete("temporary") is False


def test_per_entry_ttl_expiration(monkeypatch):
    clock = {"now": 100.0}
    monkeypatch.setattr(cache_module.time, "monotonic", lambda: clock["now"])
    cache = TTLCache(ttl_seconds=60)
    cache.set("short-lived", "value", ttl=5)
    clock["now"] = 104.99
    assert cache.get("short-lived") == "value"
    clock["now"] = 105.0
    assert cache.get("short-lived") is None


def test_ttl_seconds_keyword_and_clear_expired(monkeypatch):
    clock = {"now": 200.0}
    monkeypatch.setattr(cache_module.time, "monotonic", lambda: clock["now"])
    cache = TTLCache(ttl_seconds=60)
    cache.set("expired", "old", ttl_seconds=5)
    cache.set("active", "new", ttl_seconds=20)
    clock["now"] = 205.0
    assert cache.clear_expired() == 1
    assert cache.get("expired") is None
    assert cache.get("active") == "new"


def test_user_and_context_are_part_of_cache_key():
    common = {"reading_level": "simple", "language": "en"}
    user_one = build_cache_key("simplify_message", "Please simplify THIS", "user-1", common)
    user_two = build_cache_key("simplify_message", "Please simplify THIS", "user-2", common)
    different_context = build_cache_key(
        "simplify_message",
        "Please simplify THIS",
        "user-1",
        {"reading_level": "very_simple", "language": "en"},
    )
    assert user_one != user_two
    assert user_one != different_context


def test_equivalent_safe_input_builds_stable_key():
    first = build_cache_key("explain_message", "  What   does this mean? ", "user-1")
    second = build_cache_key("explain_message", "what does this mean?", "user-1")
    assert first == second


@pytest.mark.parametrize(
    "operation",
    ["sos", "emergency_state", "live_location", "caregiver_authorization", "safety_decision"],
)
def test_sensitive_operations_cannot_build_cache_keys(operation):
    with pytest.raises(ValueError, match="must never be cached"):
        build_cache_key(operation, "sensitive state", "user-1")
