from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.templates import find_aac_template
from app.domains.entitlements.models import UserSubscription


class Plan(str, Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    INSTITUTION = "INSTITUTION"


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    TRIAL = "TRIAL"


class Feature(str, Enum):
    AAC_BASIC = "aac.basic"
    AAC_EMERGENCY = "aac.emergency"
    AAC_BASIC_TTS = "aac.basic_tts"
    AAC_AI_GENERATION = "aac.ai_generation"
    AAC_PERSONALIZATION = "aac.personalization"
    AAC_CUSTOM_PACKS = "aac.custom_phrase_packs"
    AAC_MULTILINGUAL = "aac.multilingual_personalization"
    AAC_SAVED_PHRASES = "aac.saved_personalized_phrases"
    SENSORY_BASIC = "sensory.basic_support"
    SENSORY_HISTORY = "sensory.history"
    SENSORY_ANALYTICS = "sensory.analytics"
    ROUTINE_BASIC = "routine.basic"
    ROUTINE_ADAPTIVE = "routine.adaptive_planning"
    ROUTINE_MULTI_DAY = "routine.multi_day_planning"
    ROUTINE_ADVANCED_TRANSITIONS = "routine.advanced_transitions"
    ROUTINE_TEMPLATES = "routine.reusable_templates"
    ROUTINE_SHARED_EDITING = "routine.caregiver_shared_editing"
    ROUTINE_PERSONALIZATION = "routine.personalized_recommendations"
    SAFETY_CORE = "safety.core"
    SAFETY_STATUS = "safety.status_reporting"
    SAFETY_ONE_SAFE_ZONE = "safety.one_safe_zone"
    SAFETY_LATEST_LOCATION = "safety.latest_location"
    SAFETY_ESSENTIAL_ALERTS = "safety.essential_alerts"
    SAFETY_MULTIPLE_SAFE_ZONES = "safety.multiple_safe_zones"
    SAFETY_LOCATION_HISTORY = "safety.extended_location_history"
    SAFETY_ADVANCED_WANDERING = "safety.advanced_wandering_detection"
    SAFETY_ZONE_SCHEDULES = "safety.safe_zone_schedules"
    SAFETY_MULTIPLE_CAREGIVERS = "safety.multiple_caregiver_monitoring"
    SAFETY_TIMELINE = "safety.historical_timeline"
    SAFETY_ANALYTICS = "safety.advanced_analytics"
    CAREGIVER_INTELLIGENCE = "caregiver.advanced_analytics"
    CAREGIVER_REPORTS = "caregiver.downloadable_reports"
    CAREGIVER_MULTI_WEEK = "caregiver.multi_week_comparisons"
    INSTITUTION_ORGANIZATION = "institution.organization_management"
    INSTITUTION_STAFF = "institution.staff_accounts"
    INSTITUTION_AGGREGATE_ANALYTICS = "institution.aggregate_analytics"


@dataclass(frozen=True)
class FeatureEntitlement:
    feature: Feature
    plans: frozenset[Plan]
    critical: bool = False


FREE_FEATURES = frozenset({
    Feature.AAC_BASIC, Feature.AAC_EMERGENCY, Feature.AAC_BASIC_TTS,
    Feature.SENSORY_BASIC, Feature.ROUTINE_BASIC, Feature.SAFETY_CORE,
    Feature.SAFETY_STATUS, Feature.SAFETY_ONE_SAFE_ZONE,
    Feature.SAFETY_LATEST_LOCATION, Feature.SAFETY_ESSENTIAL_ALERTS,
})
PREMIUM_FEATURES = frozenset(
    feature for feature in Feature if not feature.value.startswith("institution.")
)
INSTITUTION_FEATURES = frozenset(Feature)
PLAN_FEATURE_ENUMS = {
    Plan.FREE: FREE_FEATURES,
    Plan.PREMIUM: PREMIUM_FEATURES,
    Plan.INSTITUTION: INSTITUTION_FEATURES,
}
CRITICAL_FEATURES = frozenset({
    Feature.AAC_EMERGENCY, Feature.SAFETY_CORE, Feature.SAFETY_STATUS,
    Feature.SAFETY_LATEST_LOCATION, Feature.SAFETY_ESSENTIAL_ALERTS,
})
FEATURE_ENTITLEMENTS = {
    feature.value: FeatureEntitlement(
        feature=feature,
        plans=frozenset(plan for plan, features in PLAN_FEATURE_ENUMS.items() if feature in features),
        critical=feature in CRITICAL_FEATURES,
    )
    for feature in Feature
}
ALWAYS_FREE_FEATURES = frozenset(feature.value for feature in FREE_FEATURES)
PLAN_FEATURES = {
    plan: frozenset(feature.value for feature in features)
    for plan, features in PLAN_FEATURE_ENUMS.items()
}
EMERGENCY_TEMPLATE_INTENTS = frozenset({"need_help", "unsafe", "call_caregiver"})


class EntitlementService:
    """Single server-side subscription and feature-access policy."""

    ACTIVE_STATUS_ALIASES = frozenset({"ACTIVE", "TRIAL", "TRIALING", "GRACE_PERIOD"})

    def __init__(self, db: Session, now=None):
        self.db = db
        self.now = now or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def _utc(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

    def get_subscription(self, user_id: str) -> Optional[UserSubscription]:
        return self.db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()

    def get_subscription_status(self, user_id: str) -> SubscriptionStatus:
        subscription = self.get_subscription(user_id)
        if subscription is None:
            return SubscriptionStatus.ACTIVE
        raw_status = str(subscription.status or "").strip().upper()
        if raw_status in {"CANCELLED", "CANCELED"}:
            return SubscriptionStatus.CANCELLED
        if raw_status == "EXPIRED":
            return SubscriptionStatus.EXPIRED
        end = subscription.expires_at or subscription.current_period_end
        if end is not None and self._utc(end) <= self._utc(self.now()):
            return SubscriptionStatus.EXPIRED
        if raw_status in {"TRIAL", "TRIALING"}:
            if subscription.trial_ends_at and self._utc(subscription.trial_ends_at) <= self._utc(self.now()):
                return SubscriptionStatus.EXPIRED
            return SubscriptionStatus.TRIAL
        return SubscriptionStatus.ACTIVE if raw_status in self.ACTIVE_STATUS_ALIASES else SubscriptionStatus.CANCELLED

    def get_plan(self, user_id: str) -> Plan:
        subscription = self.get_subscription(user_id)
        if subscription is None or self.get_subscription_status(user_id) not in {
            SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL
        }:
            return Plan.FREE
        try:
            return Plan(str(subscription.plan).upper())
        except ValueError:
            return Plan.FREE

    def has_feature_access(self, user_id: str, feature_name: str) -> bool:
        normalized = str(getattr(feature_name, "value", feature_name)).strip().lower()
        entitlement = FEATURE_ENTITLEMENTS.get(normalized)
        if entitlement is None:
            return False
        if entitlement.critical:
            return True
        return self.get_plan(user_id) in entitlement.plans

    @staticmethod
    def is_emergency_aac(text: Optional[str]) -> bool:
        template = find_aac_template(text or "")
        return bool(template and (
            template.get("safety") or template.get("intent") in EMERGENCY_TEMPLATE_INTENTS
        ))


def has_feature_access(db: Session, user_id: str, feature_name: str) -> bool:
    return EntitlementService(db).has_feature_access(user_id, feature_name)
