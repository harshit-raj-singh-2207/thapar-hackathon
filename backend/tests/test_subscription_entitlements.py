from datetime import datetime, timedelta, timezone

from app.domains.entitlements.models import UserSubscription
from app.domains.entitlements.service import (
    EntitlementService,
    Feature,
    Plan,
    SubscriptionStatus,
)
from app.domains.users.models import User


def _user(db, suffix: str):
    user = User(
        id=f"entitlement-{suffix}",
        email=f"entitlement-{suffix}@example.com",
        full_name=f"Entitlement {suffix}",
        hashed_password="not-used",
        role="caregiver",
    )
    db.add(user)
    db.commit()
    return user


def _subscribe(db, user_id: str, plan: str, status: str = "ACTIVE", **dates):
    subscription = UserSubscription(
        user_id=user_id, plan=plan, status=status, **dates
    )
    db.add(subscription)
    db.commit()
    return subscription


def test_free_access_and_premium_denial(db):
    user = _user(db, "free")
    service = EntitlementService(db)
    assert service.get_plan(user.id) is Plan.FREE
    assert service.has_feature_access(user.id, Feature.AAC_BASIC)
    assert service.has_feature_access(user.id, Feature.SENSORY_BASIC)
    assert service.has_feature_access(user.id, Feature.SAFETY_ONE_SAFE_ZONE)
    assert not service.has_feature_access(user.id, Feature.AAC_AI_GENERATION)
    assert not service.has_feature_access(user.id, Feature.SENSORY_ANALYTICS)


def test_premium_access(db):
    user = _user(db, "premium")
    _subscribe(db, user.id, "PREMIUM")
    service = EntitlementService(db)
    assert service.get_plan(user.id) is Plan.PREMIUM
    assert service.has_feature_access(user.id, Feature.AAC_AI_GENERATION)
    assert service.has_feature_access(user.id, Feature.ROUTINE_MULTI_DAY)
    assert service.has_feature_access(user.id, Feature.CAREGIVER_REPORTS)
    assert not service.has_feature_access(user.id, Feature.INSTITUTION_STAFF)


def test_institution_access(db):
    user = _user(db, "institution")
    _subscribe(db, user.id, "INSTITUTION")
    service = EntitlementService(db)
    assert service.get_plan(user.id) is Plan.INSTITUTION
    assert service.has_feature_access(user.id, Feature.SAFETY_ANALYTICS)
    assert service.has_feature_access(user.id, Feature.INSTITUTION_ORGANIZATION)
    assert service.has_feature_access(user.id, Feature.INSTITUTION_STAFF)


def test_expired_subscription_falls_back_to_free(db):
    user = _user(db, "expired")
    _subscribe(
        db,
        user.id,
        "PREMIUM",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )
    service = EntitlementService(db)
    assert service.get_subscription_status(user.id) is SubscriptionStatus.EXPIRED
    assert service.get_plan(user.id) is Plan.FREE
    assert not service.has_feature_access(user.id, Feature.SAFETY_LOCATION_HISTORY)


def test_active_trial_receives_selected_plan(db):
    user = _user(db, "trial")
    _subscribe(
        db,
        user.id,
        "PREMIUM",
        status="TRIAL",
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    service = EntitlementService(db)
    assert service.get_subscription_status(user.id) is SubscriptionStatus.TRIAL
    assert service.has_feature_access(user.id, Feature.ROUTINE_ADAPTIVE)


def test_cancelled_subscription_loses_paid_access(db):
    user = _user(db, "cancelled")
    _subscribe(db, user.id, "PREMIUM", status="CANCELLED")
    service = EntitlementService(db)
    assert service.get_subscription_status(user.id) is SubscriptionStatus.CANCELLED
    assert not service.has_feature_access(user.id, Feature.CAREGIVER_INTELLIGENCE)


def test_critical_safety_is_always_allowed(db):
    user = _user(db, "critical")
    _subscribe(db, user.id, "PREMIUM", status="EXPIRED")
    service = EntitlementService(db)
    assert service.has_feature_access(user.id, Feature.SAFETY_CORE)
    assert service.has_feature_access(user.id, Feature.SAFETY_STATUS)
    assert service.has_feature_access(user.id, Feature.SAFETY_LATEST_LOCATION)
    assert service.has_feature_access(user.id, Feature.SAFETY_ESSENTIAL_ALERTS)
    assert service.has_feature_access(user.id, Feature.AAC_EMERGENCY)


def test_unknown_feature_is_denied(db):
    user = _user(db, "unknown")
    assert not EntitlementService(db).has_feature_access(user.id, "unknown.feature")
