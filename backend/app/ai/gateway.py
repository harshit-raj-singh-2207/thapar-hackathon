import logging
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.ai.cache import (
    PROHIBITED_CACHE_OPERATIONS,
    SAFE_AI_CACHE_OPERATIONS,
    SlidingWindowRateLimiter,
    TTLCache,
    build_cache_key,
)
from app.ai.client import AIProvider, AIProviderError, create_provider
from app.ai.config import AIConfig
from app.ai.templates import find_aac_template, tokens_to_message
from app.domains.api_budget.service import APIBudgetService


logger = logging.getLogger("nivara.ai.gateway")
_shared_cache: Optional[TTLCache] = None
_shared_duplicate_cache: Optional[TTLCache] = None
_shared_limiter = SlidingWindowRateLimiter()


@dataclass
class GatewayResult:
    text: str
    source: str
    provider: str
    cached: bool = False
    budget_status: str = "NORMAL"
    fallback_reason: Optional[str] = None
    intent: Optional[str] = None
    safety_intent: bool = False
    error_code: Optional[str] = None
    http_status: Optional[int] = None


@dataclass
class BudgetCheckResult:
    allowed: bool
    status: str
    fallback: Optional[GatewayResult] = None


class SmartAIGateway:
    HIGH_VALUE_FEATURES = frozenset(
        {"simplify_message", "aac_generation", "simplify_learning_content"}
    )
    LOCAL_ONLY_FEATURES = frozenset(
        {
            "sos",
            "explicit_sos",
            "emergency_sos",
            "emergency",
            "safe",
            "unsafe",
            "safe_unsafe_selection",
            "safe_unsafe_action",
            "safety_status",
            "routine_retrieval",
            "games",
            "dashboard_loading",
            "basic_aac_template",
        }
    )

    def __init__(
        self,
        db: Session,
        provider: Optional[AIProvider] = None,
        config: Optional[AIConfig] = None,
        cache: Optional[TTLCache] = None,
        duplicate_cache: Optional[TTLCache] = None,
        rate_limiter: Optional[SlidingWindowRateLimiter] = None,
    ):
        global _shared_cache, _shared_duplicate_cache
        self.db = db
        self.config = config or AIConfig.from_settings()
        self.provider = provider or create_provider(self.config)
        if cache is None:
            if _shared_cache is None or _shared_cache.ttl_seconds != self.config.cache_ttl_seconds:
                _shared_cache = TTLCache(self.config.cache_ttl_seconds)
            cache = _shared_cache
        self.cache = cache
        if duplicate_cache is None:
            if (
                _shared_duplicate_cache is None
                or _shared_duplicate_cache.ttl_seconds != self.config.duplicate_window_seconds
            ):
                _shared_duplicate_cache = TTLCache(self.config.duplicate_window_seconds)
            duplicate_cache = _shared_duplicate_cache
        self.duplicate_cache = duplicate_cache
        self.rate_limiter = rate_limiter or _shared_limiter
        self.budget = APIBudgetService(db)
        logger.info("AI gateway initialized with provider=%s", self.provider.name)

    def generate_text(
        self,
        prompt: str,
        feature: str,
        fallback: Callable[[], str],
        user_id: Optional[str] = None,
        context: Optional[Dict[str, object]] = None,
        check_aac_template: bool = False,
        system_prompt: Optional[str] = None,
    ) -> GatewayResult:
        normalized_feature = "_".join(str(feature or "").strip().lower().split())
        local_result, cache_key = self.check_template_and_cache(
            prompt=prompt,
            feature=normalized_feature,
            user_id=user_id,
            context=context,
            check_aac_template=check_aac_template,
        )
        if local_result is not None:
            return local_result

        if normalized_feature in self.LOCAL_ONLY_FEATURES or normalized_feature in PROHIBITED_CACHE_OPERATIONS:
            logger.info("AI bypassed for local-only feature=%s", normalized_feature)
            return self._fallback(fallback, self.budget.get_budget_status(), "local_only_feature")

        # Template/cache miss: continue to the gateway's later decision stages.
        budget_check = self.check_budget(normalized_feature, fallback)
        budget_status = budget_check.status
        if not budget_check.allowed:
            return budget_check.fallback
        estimated_cost = self.config.estimated_cost_inr_per_request

        rate_key = user_id or "anonymous"
        if not self.rate_limiter.allow(rate_key, self.config.rate_limit_per_minute):
            logger.warning("AI rate limit reached user=%s", rate_key)
            result = self._fallback(fallback, budget_status, "rate_limited")
            result.error_code = "ai_rate_limit_exceeded"
            result.http_status = 429
            return result

        try:
            generated = self.provider.generate_text(prompt, system_prompt=system_prompt)
            result = GatewayResult(
                text=generated,
                source="external",
                provider=self.provider.name,
                budget_status=budget_status,
            )
            self.budget.record_api_usage(
                provider=self.provider.name,
                feature=normalized_feature,
                endpoint=self.provider.endpoint,
                estimated_cost=estimated_cost,
                user_id=user_id,
                status="success",
            )
            if cache_key is not None:
                self.cache.set(cache_key, result)
                self.duplicate_cache.set(
                    cache_key,
                    result,
                    ttl=self.config.duplicate_window_seconds,
                )
            logger.info("AI external call succeeded provider=%s feature=%s", self.provider.name, normalized_feature)
            return result
        except AIProviderError as exc:
            logger.warning("AI provider failure provider=%s feature=%s type=%s", self.provider.name, normalized_feature, type(exc).__name__)
            self._audit(normalized_feature, estimated_cost, user_id, "failed")
            return self._fallback(fallback, budget_status, type(exc).__name__)
        except Exception as exc:
            logger.exception("Unexpected AI provider failure provider=%s feature=%s", self.provider.name, feature)
            self._audit(normalized_feature, estimated_cost, user_id, "failed")
            return self._fallback(fallback, budget_status, type(exc).__name__)

    def check_template_and_cache(
        self,
        prompt: str,
        feature: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, object]] = None,
        check_aac_template: bool = False,
    ) -> Tuple[Optional[GatewayResult], Optional[str]]:
        """Resolve template/cache responses without budget or provider access.

        A miss returns ``(None, cache_key)`` so the next gateway stage can
        continue without rebuilding the safe-operation cache key.
        """
        if check_aac_template:
            template = find_aac_template(prompt)
            if template:
                logger.info("AI template hit intent=%s", template["intent"])
                return (
                    GatewayResult(
                        text=str(template["text"]),
                        source="template",
                        provider="local",
                        intent=str(template["intent"]),
                        safety_intent=bool(template.get("safety", False)),
                    ),
                    None,
                )

        cache_key = None
        if feature in SAFE_AI_CACHE_OPERATIONS:
            cache_key = build_cache_key(
                feature,
                prompt,
                user_id=user_id,
                context=context,
            )
            duplicate = self.duplicate_cache.get(cache_key)
            if duplicate is not None:
                logger.info("AI duplicate request reused feature=%s", feature)
                duplicate.cached = True
                duplicate.source = "duplicate_cache"
                return duplicate, cache_key
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info("AI cache hit feature=%s", feature)
                cached.cached = True
                cached.source = "cache"
                return cached, cache_key
        return None, cache_key

    def check_budget(
        self,
        feature: str,
        fallback: Callable[[], str],
    ) -> BudgetCheckResult:
        """Evaluate the existing budget service without invoking the AI provider."""
        normalized_feature = "_".join(str(feature or "").strip().lower().split())
        if (
            normalized_feature in self.LOCAL_ONLY_FEATURES
            or normalized_feature in PROHIBITED_CACHE_OPERATIONS
            or self.budget.is_safety_bypass(normalized_feature)
        ):
            return BudgetCheckResult(
                allowed=False,
                status="NOT_APPLICABLE",
                fallback=self._fallback(fallback, "NOT_APPLICABLE", "local_only_feature"),
            )

        budget_status = self.budget.get_budget_status()
        allowed = self._state_allows(normalized_feature, budget_status) and self.budget.can_use_api(
            self.provider.name,
            normalized_feature,
            self.config.estimated_cost_inr_per_request,
        )
        if allowed:
            return BudgetCheckResult(allowed=True, status=budget_status)

        logger.warning("AI budget denied feature=%s state=%s", normalized_feature, budget_status)
        return BudgetCheckResult(
            allowed=False,
            status=budget_status,
            fallback=self._fallback(fallback, budget_status, "budget_denied"),
        )

    def build_aac_sentence(
        self,
        tokens=None,
        sentence: Optional[str] = None,
        user_id: Optional[str] = None,
        fallback: Optional[Callable[[], str]] = None,
        context: Optional[Dict[str, object]] = None,
    ) -> GatewayResult:
        message = tokens_to_message(tokens, sentence)
        local_fallback = fallback or (lambda: message or "I need assistance.")
        return self.generate_text(
            prompt=message,
            feature="aac_generation",
            fallback=local_fallback,
            user_id=user_id,
            context=context,
            check_aac_template=True,
            system_prompt="Create one short, clear, respectful AAC sentence. Return only the sentence.",
        )

    def simplify_message(
        self,
        text: str,
        user_id: Optional[str] = None,
        fallback: Optional[Callable[[], str]] = None,
        context: Optional[Dict[str, object]] = None,
    ) -> GatewayResult:
        return self.generate_text(
            prompt=text,
            feature="simplify_message",
            fallback=fallback or (lambda: text),
            user_id=user_id,
            context=context,
            system_prompt="Simplify this into short, literal, autism-friendly language. Return only the simplified text.",
        )

    def explain_message(
        self,
        text: str,
        user_id: Optional[str] = None,
        fallback: Optional[Callable[[], str]] = None,
        context: Optional[Dict[str, object]] = None,
    ) -> GatewayResult:
        return self.generate_text(
            prompt=text,
            feature="personalized_explanation",
            fallback=fallback or (lambda: text),
            user_id=user_id,
            context=context,
            system_prompt="Give a short, concrete, child-friendly explanation. Avoid figurative or alarming language.",
        )

    def _audit(self, feature: str, cost, user_id: Optional[str], status: str) -> None:
        self.budget.record_api_usage(
            provider=self.provider.name,
            feature=feature,
            endpoint=self.provider.endpoint,
            estimated_cost=cost,
            user_id=user_id,
            status=status,
        )

    def _fallback(self, fallback: Callable[[], str], budget_status: str, reason: str) -> GatewayResult:
        return GatewayResult(
            text=fallback(),
            source="local_fallback",
            provider="local",
            budget_status=budget_status,
            fallback_reason=reason,
        )

    @classmethod
    def _state_allows(cls, feature: str, status: str) -> bool:
        if status in {"BLOCK_OPTIONAL_APIS", "EMERGENCY"}:
            return False
        if status == "RESTRICTED":
            return feature in cls.HIGH_VALUE_FEATURES
        return True
