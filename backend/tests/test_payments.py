import json
import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.domains.entitlements.models import UserSubscription
from app.domains.entitlements.service import EntitlementService, Feature, Plan
from app.domains.payments.provider import ProviderVerification
from app.domains.payments.router import get_payment_service
from app.domains.payments.service import PaymentService
from app.main import app
from app.models.user import User


client = TestClient(app)


class FakePaymentProvider:
    name = "fakepay"
    public_key = "public_test_key"

    def __init__(self, verified=True):
        self.verified = verified
        self.checkout_calls = 0

    def create_checkout(self, **kwargs):
        self.checkout_calls += 1
        return {"id": f"order_{uuid.uuid4().hex}"}

    def verify_payment(self, **kwargs):
        return ProviderVerification(self.verified, "captured" if self.verified else "invalid_signature")

    def handle_webhook(self, *, payload, signature):
        if signature != "valid-webhook":
            raise AssertionError("Test webhook signature was not verified")
        return json.loads(payload)

    def cancel_subscription(self, provider_subscription_id):
        return {"id": provider_subscription_id, "status": "cancelled"}


def _account(db, suffix):
    user = User(
        id=f"payment-user-{suffix}", email=f"payment-{suffix}@example.com",
        full_name=f"Payment {suffix}", hashed_password="unused", role="caregiver",
    )
    db.add(user)
    db.commit()
    return user, {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _override(provider):
    def dependency():
        session = SessionLocal()
        try:
            yield PaymentService(session, provider=provider)
        finally:
            session.close()
    app.dependency_overrides[get_payment_service] = dependency


def _checkout(headers):
    return client.post("/api/v1/payments/checkout", json={"plan_id": "PREMIUM"}, headers=headers)


def test_checkout_creation_uses_backend_price(db):
    _, headers = _account(db, "checkout")
    provider = FakePaymentProvider()
    _override(provider)
    try:
        response = _checkout(headers)
        assert response.status_code == 200
        assert response.json()["amount"] == int(round(settings.PREMIUM_MONTHLY_PRICE_INR * 100))
        assert response.json()["key_id"] == "public_test_key"
        assert "secret" not in response.text.lower()
    finally:
        app.dependency_overrides.clear()


def test_valid_verification_activates_premium(db):
    user, headers = _account(db, "valid")
    _override(FakePaymentProvider(verified=True))
    try:
        order_id = _checkout(headers).json()["order_id"]
        response = client.post(
            "/api/v1/payments/verify",
            json={"order_id": order_id, "payment_id": "payment_valid", "signature": "provider-signature"},
            headers=headers,
        )
        db.expire_all()
        assert response.status_code == 200
        assert response.json()["verified"] is True
        assert EntitlementService(db).get_plan(user.id) is Plan.PREMIUM
        assert EntitlementService(db).has_feature_access(user.id, Feature.AAC_AI_GENERATION)
    finally:
        app.dependency_overrides.clear()


def test_invalid_verification_does_not_unlock_premium(db):
    user, headers = _account(db, "invalid")
    _override(FakePaymentProvider(verified=False))
    try:
        order_id = _checkout(headers).json()["order_id"]
        response = client.post(
            "/api/v1/payments/verify",
            json={"order_id": order_id, "payment_id": "payment_bad", "signature": "bad"},
            headers=headers,
        )
        db.expire_all()
        assert response.json()["verified"] is False
        assert db.query(UserSubscription).filter(UserSubscription.user_id == user.id).first() is None
        assert EntitlementService(db).get_plan(user.id) is Plan.FREE
    finally:
        app.dependency_overrides.clear()


def test_duplicate_webhook_is_idempotent(db):
    user, headers = _account(db, "webhook")
    _override(FakePaymentProvider())
    try:
        checkout = _checkout(headers).json()
        payload = {
            "event": "payment.captured",
            "payload": {"payment": {"entity": {
                "id": "payment_webhook", "order_id": checkout["order_id"],
                "amount": checkout["amount"],
            }}},
        }
        first = client.post("/api/v1/payments/webhook", content=json.dumps(payload), headers={"X-Razorpay-Signature": "valid-webhook"})
        db.expire_all()
        first_expiry = db.query(UserSubscription).filter(UserSubscription.user_id == user.id).one().expires_at
        second = client.post("/api/v1/payments/webhook", content=json.dumps(payload), headers={"X-Razorpay-Signature": "valid-webhook"})
        db.expire_all()
        second_expiry = db.query(UserSubscription).filter(UserSubscription.user_id == user.id).one().expires_at
        assert first.json()["verified"] is True
        assert second.json()["message"] == "Payment was already processed."
        assert first_expiry == second_expiry
    finally:
        app.dependency_overrides.clear()


def test_missing_payment_configuration_is_safe(db, monkeypatch):
    _, headers = _account(db, "config")
    app.dependency_overrides.clear()
    monkeypatch.setattr(settings, "PAYMENT_KEY_ID", "")
    monkeypatch.setattr(settings, "PAYMENT_KEY_SECRET", "")
    response = _checkout(headers)
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()
