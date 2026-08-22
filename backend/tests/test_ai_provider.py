import json
from dataclasses import replace
from urllib import error

import pytest

from app.ai.client import (
    AIProvider,
    AIProviderError,
    AIProviderInvalidResponse,
    AIProviderTimeout,
    AIProviderUnavailable,
    DisabledProvider,
    GroqProvider,
    create_provider,
)
from app.ai.config import AIConfig


def provider_config(**changes):
    base = AIConfig(
        provider="groq",
        model="test-model",
        api_key="server-secret-for-mocked-test",
        request_timeout_seconds=3,
        max_output_tokens=80,
        rate_limit_per_minute=10,
        cache_ttl_seconds=60,
        estimated_cost_inr_per_request=0.05,
    )
    return replace(base, **changes)


class MockHTTPResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


class RecordingProvider(AIProvider):
    name = "recording"

    def __init__(self):
        self.calls = []

    def generate_text(self, prompt, system_prompt=None):
        self.calls.append((prompt, system_prompt))
        return "controlled result"


def test_groq_generate_text_uses_environment_config_and_parses_response(monkeypatch):
    captured = {}

    def fake_urlopen(api_request, timeout):
        captured["request"] = api_request
        captured["timeout"] = timeout
        response = {"choices": [{"message": {"content": "  Clear response  "}}]}
        return MockHTTPResponse(json.dumps(response).encode("utf-8"))

    monkeypatch.setattr("app.ai.client.request.urlopen", fake_urlopen)
    config = provider_config()
    result = GroqProvider(config).generate_text("Hello", "Be concise")

    assert result == "Clear response"
    assert captured["timeout"] == config.request_timeout_seconds
    payload = json.loads(captured["request"].data.decode("utf-8"))
    assert payload["model"] == config.model
    assert payload["max_tokens"] == config.max_output_tokens
    assert payload["messages"] == [
        {"role": "system", "content": "Be concise"},
        {"role": "user", "content": "Hello"},
    ]


def test_provider_independent_convenience_methods():
    provider = RecordingProvider()
    assert provider.simplify_message("Complex sentence") == "controlled result"
    assert provider.explain_message("New idea") == "controlled result"
    assert provider.build_aac_sentence(["I", "NEED", "HELP"]) == "controlled result"
    assert [call[0] for call in provider.calls] == ["Complex sentence", "New idea", "I NEED HELP"]
    assert all(call[1] for call in provider.calls)


def test_empty_aac_tokens_return_controlled_error():
    with pytest.raises(AIProviderError, match="At least one AAC token"):
        RecordingProvider().build_aac_sentence([])


def test_missing_api_key_returns_controlled_error(monkeypatch):
    monkeypatch.setattr(
        "app.ai.client.request.urlopen",
        lambda *args, **kwargs: pytest.fail("Network must not be called without an API key"),
    )
    with pytest.raises(AIProviderUnavailable, match="credentials are not configured"):
        GroqProvider(provider_config(api_key="")).generate_text("Hello")


def test_timeout_returns_controlled_error(monkeypatch):
    monkeypatch.setattr(
        "app.ai.client.request.urlopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError()),
    )
    with pytest.raises(AIProviderTimeout, match="timed out"):
        GroqProvider(provider_config()).generate_text("Hello")


def test_network_failure_returns_controlled_error(monkeypatch):
    monkeypatch.setattr(
        "app.ai.client.request.urlopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(error.URLError("offline")),
    )
    with pytest.raises(AIProviderUnavailable, match="unavailable"):
        GroqProvider(provider_config()).generate_text("Hello")


@pytest.mark.parametrize(
    "body",
    [
        b"not-json",
        json.dumps({"choices": []}).encode("utf-8"),
        json.dumps({"choices": [{"message": {"content": ""}}]}).encode("utf-8"),
    ],
)
def test_invalid_provider_response_returns_controlled_error(monkeypatch, body):
    monkeypatch.setattr(
        "app.ai.client.request.urlopen",
        lambda *args, **kwargs: MockHTTPResponse(body),
    )
    with pytest.raises(AIProviderInvalidResponse):
        GroqProvider(provider_config()).generate_text("Hello")


def test_provider_factory_keeps_groq_and_disables_unknown_provider():
    assert isinstance(create_provider(provider_config(provider="groq")), GroqProvider)
    assert isinstance(create_provider(provider_config(provider="unknown")), DisabledProvider)
