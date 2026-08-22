from dataclasses import replace

import pytest

from app.ai import cache as cache_module
from app.ai.cache import SlidingWindowRateLimiter, TTLCache, build_cache_key
from app.ai.client import AIProvider, AIProviderTimeout, GroqProvider
from app.ai.config import AIConfig
from app.ai.gateway import GatewayResult, SmartAIGateway
from app.domains.api_budget.models import APIUsageRecord


class FakeProvider(AIProvider):
    name = "groq"
    endpoint = "https://mock.groq.test/chat"

    def __init__(self, response="External response", error=None):
        self.response = response
        self.error = error
        self.calls = 0

    def generate_text(self, prompt, system_prompt=None):
        del prompt, system_prompt
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def config(**changes):
    base = AIConfig(
        provider="groq",
        model="test-model",
        api_key="test-key",
        request_timeout_seconds=1,
        max_output_tokens=50,
        rate_limit_per_minute=10,
        cache_ttl_seconds=60,
        estimated_cost_inr_per_request=0.05,
    )
    return replace(base, **changes)


def gateway(db, provider=None, ai_config=None):
    selected_config = ai_config or config()
    return SmartAIGateway(
        db,
        provider=provider or FakeProvider(),
        config=selected_config,
        cache=TTLCache(60),
        duplicate_cache=TTLCache(selected_config.duplicate_window_seconds),
        rate_limiter=SlidingWindowRateLimiter(),
    )


def test_gateway_initializes_with_existing_dependencies(db):
    provider = FakeProvider()
    ai_config = config(duplicate_window_seconds=12)
    response_cache = TTLCache(45)
    duplicate_cache = TTLCache(12)
    limiter = SlidingWindowRateLimiter()

    ai = SmartAIGateway(
        db,
        provider=provider,
        config=ai_config,
        cache=response_cache,
        duplicate_cache=duplicate_cache,
        rate_limiter=limiter,
    )

    assert ai.db is db
    assert ai.provider is provider
    assert ai.config is ai_config
    assert ai.cache is response_cache
    assert ai.duplicate_cache is duplicate_cache
    assert ai.rate_limiter is limiter
    assert ai.budget.db is db
    assert provider.calls == 0


def test_gateway_exposes_provider_neutral_interface(db):
    ai = gateway(db)
    assert callable(ai.generate_text)
    assert callable(ai.simplify_message)
    assert callable(ai.explain_message)
    assert callable(ai.build_aac_sentence)


def test_aac_template_response_never_calls_external_api(db):
    provider = FakeProvider()
    result = gateway(db, provider).build_aac_sentence(
        sentence="help me",
        fallback=lambda: "fallback",
    )
    assert result.source == "template"
    assert result.text == "I need help, please."
    assert provider.calls == 0
    assert db.query(APIUsageRecord).count() == 0


def test_template_cache_stage_exact_template_hit_uses_no_paid_stage(db, monkeypatch):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)
    monkeypatch.setattr(ai.budget, "get_budget_status", lambda *args: pytest.fail("budget must not be used"))

    result, cache_key = ai.check_template_and_cache(
        "I need help",
        feature="aac_generation",
        check_aac_template=True,
    )

    assert result is not None
    assert result.source == "template"
    assert result.intent == "need_help"
    assert cache_key is None
    assert provider.calls == 0


def test_template_cache_stage_normalized_template_hit(db, monkeypatch):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)
    monkeypatch.setattr(ai.budget, "get_budget_status", lambda *args: pytest.fail("budget must not be used"))

    result, _ = ai.check_template_and_cache(
        "  HELP   ME!!! ",
        feature="aac_generation",
        check_aac_template=True,
    )

    assert result is not None
    assert result.intent == "need_help"
    assert provider.calls == 0


def test_cache_hit_avoids_second_external_call(db):
    provider = FakeProvider("Simplified externally")
    ai = gateway(db, provider)
    first = ai.simplify_message("A complicated unique message", fallback=lambda: "local")
    second = ai.simplify_message("A complicated unique message", fallback=lambda: "local")
    assert first.source == "external"
    assert second.source == "duplicate_cache"
    assert second.cached is True
    assert provider.calls == 1


def test_prepopulated_cache_hit_never_calls_provider(db):
    provider = FakeProvider("must not be used")
    ai = gateway(db, provider)
    cache_key = build_cache_key(
        "simplify_message",
        "A cached request",
        user_id="user-1",
        context={"language": "en"},
    )
    ai.cache.set(
        cache_key,
        GatewayResult(
            text="Cached response",
            source="external",
            provider="groq",
        ),
    )

    result = ai.simplify_message(
        "A cached request",
        user_id="user-1",
        context={"language": "en"},
    )

    assert result.text == "Cached response"
    assert result.source == "cache"
    assert result.cached is True
    assert provider.calls == 0
    assert db.query(APIUsageRecord).count() == 0


def test_template_cache_stage_cache_hit_uses_no_paid_stage(db, monkeypatch):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)
    cache_key = build_cache_key("simplify_message", "cached input", user_id="user-1")
    ai.cache.set(cache_key, GatewayResult("cached", "external", "groq"))
    monkeypatch.setattr(ai.budget, "get_budget_status", lambda *args: pytest.fail("budget must not be used"))

    result, returned_key = ai.check_template_and_cache(
        "cached input",
        feature="simplify_message",
        user_id="user-1",
    )

    assert result is not None
    assert result.text == "cached"
    assert result.source == "cache"
    assert returned_key == cache_key
    assert provider.calls == 0


def test_template_cache_stage_miss_continues_without_paid_stage(db, monkeypatch):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)
    monkeypatch.setattr(ai.budget, "get_budget_status", lambda *args: pytest.fail("budget must not be used"))

    result, cache_key = ai.check_template_and_cache(
        "a unique uncached input",
        feature="simplify_message",
        user_id="user-1",
    )

    assert result is None
    assert cache_key == build_cache_key(
        "simplify_message",
        "a unique uncached input",
        user_id="user-1",
    )
    assert provider.calls == 0


def test_budget_allowed_calls_provider_and_records_usage(db):
    provider = FakeProvider("Clear external answer")
    result = gateway(db, provider).generate_text(
        "Explain this unusual situation",
        feature="personalized_explanation",
        fallback=lambda: "local answer",
        user_id="user-verified-sarah",
    )
    assert result.text == "Clear external answer"
    assert provider.calls == 1
    usage = db.query(APIUsageRecord).one()
    assert usage.provider == "groq"
    assert usage.feature == "personalized_explanation"
    assert float(usage.estimated_cost) == 0.05


def test_budget_stage_allows_without_calling_provider(db):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)

    decision = ai.check_budget("simplify_message", fallback=lambda: "local")

    assert decision.allowed is True
    assert decision.status == "NORMAL"
    assert decision.fallback is None
    assert provider.calls == 0


def test_budget_stage_denial_returns_local_fallback_without_provider(db):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)
    ai.budget.record_api_usage("groq", "seed", "/seed", 1500, status="success")

    decision = ai.check_budget("simplify_message", fallback=lambda: "local budget fallback")

    assert decision.allowed is False
    assert decision.status == "BLOCK_OPTIONAL_APIS"
    assert decision.fallback is not None
    assert decision.fallback.text == "local budget fallback"
    assert decision.fallback.source == "local_fallback"
    assert decision.fallback.fallback_reason == "budget_denied"
    assert provider.calls == 0


@pytest.mark.parametrize("feature", ["sos", "explicit_sos", "unsafe", "safety_status", "emergency"])
def test_safety_actions_bypass_budget_and_provider(db, monkeypatch, feature):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider)
    monkeypatch.setattr(ai.budget, "get_budget_status", lambda *args: pytest.fail("budget must not be used"))
    monkeypatch.setattr(ai.budget, "can_use_api", lambda *args: pytest.fail("budget must not be used"))

    decision = ai.check_budget(feature, fallback=lambda: "local safety action")

    assert decision.allowed is False
    assert decision.status == "NOT_APPLICABLE"
    assert decision.fallback is not None
    assert decision.fallback.text == "local safety action"
    assert decision.fallback.fallback_reason == "local_only_feature"
    assert provider.calls == 0


def test_restricted_budget_does_not_call_optional_provider(db):
    provider = FakeProvider()
    ai = gateway(db, provider)
    ai.budget.record_api_usage("groq", "seed", "/seed", 1275, status="success")
    result = ai.explain_message("Optional personalized explanation", fallback=lambda: "local explanation")
    assert ai.budget.get_budget_status() == "RESTRICTED"
    assert result.text == "local explanation"
    assert result.fallback_reason == "budget_denied"
    assert provider.calls == 0


def test_budget_denial_does_not_record_an_api_call(db):
    provider = FakeProvider()
    ai = gateway(db, provider)
    ai.budget.record_api_usage("groq", "seed", "/seed", 1500, status="success")
    before = db.query(APIUsageRecord).count()
    result = ai.simplify_message("A unique request over budget", fallback=lambda: "local")
    assert result.fallback_reason == "budget_denied"
    assert provider.calls == 0
    assert db.query(APIUsageRecord).count() == before


def test_provider_timeout_returns_fallback(db):
    provider = FakeProvider(error=AIProviderTimeout("timeout"))
    result = gateway(db, provider).simplify_message("Unique timeout input", fallback=lambda: "safe fallback")
    assert result.text == "safe fallback"
    assert result.source == "local_fallback"
    assert result.fallback_reason == "AIProviderTimeout"
    assert provider.calls == 1


def test_missing_api_key_returns_graceful_fallback(db):
    missing_key_config = config(api_key="")
    provider = GroqProvider(missing_key_config)
    result = gateway(db, provider, missing_key_config).explain_message(
        "Unique missing key input",
        fallback=lambda: "local without key",
    )
    assert result.text == "local without key"
    assert result.source == "local_fallback"


def test_duplicate_request_is_deduplicated_by_cache(db):
    provider = FakeProvider("one charged result")
    ai = gateway(db, provider)
    for _ in range(3):
        result = ai.generate_text(
            "identical rapid request",
            feature="generate_communication_suggestion",
            fallback=lambda: "local",
            user_id="same-user",
        )
    assert result.cached is True
    assert provider.calls == 1
    assert db.query(APIUsageRecord).filter(APIUsageRecord.status == "success").count() == 1


def test_ai_rate_limit_uses_fallback_without_second_provider_call(db):
    provider = FakeProvider("first result")
    ai = gateway(db, provider, config(rate_limit_per_minute=1))
    first = ai.generate_text("first unique prompt", "personalized_explanation", lambda: "first local", user_id="u1")
    second = ai.generate_text("second unique prompt", "personalized_explanation", lambda: "rate fallback", user_id="u1")
    assert first.source == "external"
    assert second.text == "rate fallback"
    assert second.fallback_reason == "rate_limited"
    assert second.error_code == "ai_rate_limit_exceeded"
    assert second.http_status == 429
    assert provider.calls == 1
    assert db.query(APIUsageRecord).filter(APIUsageRecord.status == "success").count() == 1


def test_multiple_requests_within_limit_call_provider(db):
    provider = FakeProvider("external")
    ai = gateway(db, provider, config(rate_limit_per_minute=2))

    first = ai.simplify_message("allowed request one", user_id="u1")
    second = ai.simplify_message("allowed request two", user_id="u1")

    assert first.source == "external"
    assert second.source == "external"
    assert provider.calls == 2
    assert db.query(APIUsageRecord).filter(APIUsageRecord.status == "success").count() == 2


def test_regular_cache_hit_bypasses_exhausted_rate_limit(db):
    provider = FakeProvider("external")
    ai = gateway(db, provider, config(rate_limit_per_minute=1))
    first = ai.simplify_message("consume the only slot", user_id="u1")
    cache_key = build_cache_key("simplify_message", "already cached", user_id="u1")
    ai.cache.set(cache_key, GatewayResult("cached response", "external", "groq"))

    cached = ai.simplify_message("already cached", user_id="u1")

    assert first.source == "external"
    assert cached.source == "cache"
    assert cached.text == "cached response"
    assert cached.http_status is None
    assert provider.calls == 1


def test_duplicate_request_does_not_consume_another_rate_limit_slot(db):
    provider = FakeProvider("protected response")
    ai = gateway(db, provider, config(rate_limit_per_minute=2, duplicate_window_seconds=10))
    first = ai.simplify_message("repeat this request", user_id="same-user")
    duplicate = ai.simplify_message("repeat this request", user_id="same-user")
    second_external = ai.simplify_message("another request", user_id="same-user")
    assert first.source == "external"
    assert duplicate.source == "duplicate_cache"
    assert duplicate.cached is True
    assert second_external.source == "external"
    assert provider.calls == 2
    assert db.query(APIUsageRecord).filter(APIUsageRecord.status == "success").count() == 2


def test_different_users_have_independent_rate_limits(db):
    provider = FakeProvider("external")
    ai = gateway(db, provider, config(rate_limit_per_minute=1))

    user_one = ai.simplify_message("user one request", user_id="user-1")
    user_two = ai.simplify_message("user two request", user_id="user-2")

    assert user_one.source == "external"
    assert user_two.source == "external"
    assert provider.calls == 2


def test_different_requests_are_not_treated_as_duplicates(db):
    provider = FakeProvider("external response")
    ai = gateway(db, provider, config(duplicate_window_seconds=10))

    first = ai.simplify_message("first unique request", user_id="same-user")
    second = ai.simplify_message("second unique request", user_id="same-user")

    assert first.source == "external"
    assert second.source == "external"
    assert provider.calls == 2


def test_same_request_from_different_users_is_not_a_duplicate(db):
    provider = FakeProvider("external response")
    ai = gateway(db, provider, config(duplicate_window_seconds=10))

    first = ai.simplify_message("shared input", user_id="user-1")
    second = ai.simplify_message("shared input", user_id="user-2")

    assert first.source == "external"
    assert second.source == "external"
    assert provider.calls == 2


def test_same_input_with_different_operations_is_not_a_duplicate(db):
    provider = FakeProvider("external response")
    ai = gateway(db, provider, config(duplicate_window_seconds=10))

    simplified = ai.simplify_message("Hello", user_id="user-1")
    explained = ai.explain_message("Hello", user_id="user-1")

    assert simplified.source == "external"
    assert explained.source == "external"
    assert provider.calls == 2
    assert db.query(APIUsageRecord).filter(APIUsageRecord.status == "success").count() == 2


def test_request_after_duplicate_window_is_not_a_duplicate(db, monkeypatch):
    clock = {"now": 100.0}
    monkeypatch.setattr(cache_module.time, "monotonic", lambda: clock["now"])
    provider = FakeProvider("external response")
    ai_config = config(duplicate_window_seconds=10)
    ai = SmartAIGateway(
        db,
        provider=provider,
        config=ai_config,
        # Use a shorter normal cache TTL so this test isolates duplicate expiry.
        cache=TTLCache(5),
        duplicate_cache=TTLCache(ai_config.duplicate_window_seconds),
        rate_limiter=SlidingWindowRateLimiter(),
    )

    first = ai.simplify_message("expiring duplicate", user_id="user-1")
    clock["now"] = 111.0
    after_window = ai.simplify_message("expiring duplicate", user_id="user-1")

    assert first.source == "external"
    assert after_window.source == "external"
    assert provider.calls == 2
    assert db.query(APIUsageRecord).filter(APIUsageRecord.status == "success").count() == 2


def test_local_template_bypasses_exhausted_rate_limit(db):
    provider = FakeProvider("external")
    ai = gateway(db, provider, config(rate_limit_per_minute=1))
    ai.simplify_message("first external request", user_id="u1")
    result = ai.build_aac_sentence(sentence="help me", user_id="u1")
    assert result.source == "template"
    assert result.text == "I need help, please."
    assert result.http_status is None
    assert provider.calls == 1


def test_repeated_template_request_stays_local(db):
    provider = FakeProvider("must not be called")
    ai = gateway(db, provider, config(duplicate_window_seconds=10))

    first = ai.build_aac_sentence(sentence="help me", user_id="user-1")
    second = ai.build_aac_sentence(sentence="help me", user_id="user-1")

    assert first.source == "template"
    assert second.source == "template"
    assert provider.calls == 0


def test_safety_template_is_deterministic_and_marked(db):
    provider = FakeProvider()
    result = gateway(db, provider).build_aac_sentence(sentence="I feel unsafe", fallback=lambda: "fallback")
    assert result.source == "template"
    assert result.safety_intent is True
    assert result.intent == "unsafe"
    assert provider.calls == 0


def test_local_only_feature_never_calls_provider_or_records_usage(db):
    provider = FakeProvider()
    ai = gateway(db, provider)
    result = ai.generate_text(
        "load the dashboard",
        feature="dashboard_loading",
        fallback=lambda: "local dashboard data",
    )
    assert result.text == "local dashboard data"
    assert result.fallback_reason == "local_only_feature"
    assert provider.calls == 0
    assert db.query(APIUsageRecord).count() == 0


def test_unsafe_status_selection_never_calls_provider(db):
    provider = FakeProvider()
    result = gateway(db, provider).generate_text(
        "unsafe",
        feature="safety_status",
        fallback=lambda: "unsafe",
    )
    assert result.text == "unsafe"
    assert result.source == "local_fallback"
    assert provider.calls == 0
