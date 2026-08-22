from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class AIConfig:
    provider: str
    model: str
    api_key: str
    request_timeout_seconds: float
    max_output_tokens: int
    rate_limit_per_minute: int
    cache_ttl_seconds: int
    estimated_cost_inr_per_request: float
    duplicate_window_seconds: int = 10

    @classmethod
    def from_settings(cls) -> "AIConfig":
        return cls(
            provider=settings.AI_PROVIDER.strip().lower(),
            model=settings.AI_MODEL.strip(),
            api_key=settings.AI_API_KEY.strip(),
            request_timeout_seconds=settings.AI_REQUEST_TIMEOUT_SECONDS,
            max_output_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            rate_limit_per_minute=settings.AI_RATE_LIMIT_PER_MINUTE,
            cache_ttl_seconds=settings.AI_CACHE_TTL_SECONDS,
            estimated_cost_inr_per_request=settings.AI_ESTIMATED_COST_INR_PER_REQUEST,
            duplicate_window_seconds=settings.AI_DUPLICATE_WINDOW_SECONDS,
        )
