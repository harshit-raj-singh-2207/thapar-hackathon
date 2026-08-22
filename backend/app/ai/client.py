import json
from abc import ABC, abstractmethod
from typing import Iterable, Optional
from urllib import error, request

from app.ai.config import AIConfig


class AIProviderError(RuntimeError):
    pass


class AIProviderTimeout(AIProviderError):
    pass


class AIProviderUnavailable(AIProviderError):
    pass


class AIProviderInvalidResponse(AIProviderError):
    pass


class AIProvider(ABC):
    name = "unknown"
    endpoint = ""

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        raise NotImplementedError

    def simplify_message(self, message: str) -> str:
        return self.generate_text(
            message,
            system_prompt=(
                "Simplify this into short, literal, autism-friendly language. "
                "Preserve the meaning and return only the simplified message."
            ),
        )

    def explain_message(self, message: str) -> str:
        return self.generate_text(
            message,
            system_prompt=(
                "Explain this with short, concrete, child-friendly language. "
                "Avoid figurative, ambiguous, or alarming wording."
            ),
        )

    def build_aac_sentence(self, tokens: Iterable[str]) -> str:
        token_text = " ".join(str(token).strip() for token in tokens if str(token).strip())
        if not token_text:
            raise AIProviderError("At least one AAC token is required.")
        return self.generate_text(
            token_text,
            system_prompt=(
                "Turn these AAC tokens into one short, clear, respectful sentence. "
                "Preserve the intended meaning and return only the sentence."
            ),
        )


class GroqProvider(AIProvider):
    """Small OpenAI-compatible Groq client using the Python standard library."""

    name = "groq"
    endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, config: AIConfig):
        self.config = config

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.config.api_key:
            raise AIProviderUnavailable("AI provider credentials are not configured.")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps(
            {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_output_tokens,
                "temperature": 0.2,
            }
        ).encode("utf-8")
        api_request = request.Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(api_request, timeout=self.config.request_timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except TimeoutError as exc:
            raise AIProviderTimeout("AI provider request timed out.") from exc
        except error.HTTPError as exc:
            raise AIProviderUnavailable(f"AI provider request failed with HTTP status {exc.code}.") from exc
        except error.URLError as exc:
            if isinstance(exc, TimeoutError) or isinstance(getattr(exc, "reason", None), TimeoutError):
                raise AIProviderTimeout("AI provider request timed out.") from exc
            raise AIProviderUnavailable("AI provider is unavailable.") from exc
        except (ValueError, UnicodeDecodeError) as exc:
            raise AIProviderInvalidResponse("AI provider returned malformed JSON.") from exc

        try:
            text = body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise AIProviderInvalidResponse("AI provider response did not contain generated text.") from exc
        if not text:
            raise AIProviderInvalidResponse("AI provider returned an empty response.")
        return text


class DisabledProvider(AIProvider):
    name = "disabled"
    endpoint = "local://disabled"

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        del prompt, system_prompt
        raise AIProviderUnavailable("External AI is disabled or not configured.")


def create_provider(config: AIConfig) -> AIProvider:
    if config.provider == "groq":
        return GroqProvider(config)
    return DisabledProvider()
