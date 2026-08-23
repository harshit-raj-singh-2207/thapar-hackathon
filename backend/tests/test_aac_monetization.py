from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.ai.gateway import GatewayResult
from app.core.database import get_db
from app.dependencies.auth import get_optional_user
from app.domains.entitlements.models import UserSubscription
from app.domains.entitlements.service import EntitlementService, Feature, Plan
from app.main import app


client = TestClient(app)
USER_ID = "user-verified-sarah"


def _user():
    return SimpleNamespace(id=USER_ID, role="caregiver")


def _overrides(db):
    def database():
        yield db
    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_optional_user] = _user


def _subscribe(db, plan=Plan.PREMIUM):
    db.add(UserSubscription(user_id=USER_ID, plan=plan.value, status="active"))
    db.commit()


def test_free_basic_aac_is_local_and_available(db, monkeypatch):
    _overrides(db)
    monkeypatch.setattr(
        "app.domains.communication.aac_service.SmartAIGateway",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("gateway called")),
    )
    try:
        response = client.post(
            "/api/v1/communication/aac/sentence",
            json={"tokens": ["I", "NEED", "HELP"], "save_log": False},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "help" in response.json()["generated_sentence"].lower()


def test_premium_user_can_use_ai_aac_through_gateway(db, monkeypatch):
    _subscribe(db)
    _overrides(db)

    class Gateway:
        def __init__(self, gateway_db):
            assert gateway_db is db

        def build_aac_sentence(self, **kwargs):
            return GatewayResult(
                text="A personalized sentence.", source="external", provider="groq"
            )

    monkeypatch.setattr("app.domains.communication.service.SmartAIGateway", Gateway)
    try:
        response = client.post(
            "/api/v1/communication/sentence/generate",
            json={"sentence": "share a unique thought"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["generated_sentence"] == "A personalized sentence."


def test_free_user_is_denied_premium_personalization(db):
    _overrides(db)
    try:
        response = client.post(
            "/api/v1/communication/simplify",
            json={"text": "Please personalize this complex message."},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "premium_feature_required"


def test_emergency_aac_is_always_free(db, monkeypatch):
    _overrides(db)

    def must_not_check(*_args, **_kwargs):
        raise AssertionError("emergency entitlement was checked")

    monkeypatch.setattr(EntitlementService, "has_feature_access", must_not_check)
    try:
        response = client.post(
            "/api/v1/communication/sentence/generate",
            json={"sentence": "I feel unsafe"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "unsafe" in response.json()["generated_sentence"].lower()


def test_ai_budget_block_returns_safe_local_fallback_for_premium(db, monkeypatch):
    _subscribe(db)
    _overrides(db)

    class BudgetBlockedGateway:
        def __init__(self, gateway_db):
            assert gateway_db is db

        def build_aac_sentence(self, **kwargs):
            return GatewayResult(
                text=kwargs["fallback"](),
                source="local_fallback",
                provider="local",
                budget_status="BLOCK_OPTIONAL_APIS",
                fallback_reason="budget_denied",
            )

    monkeypatch.setattr(
        "app.domains.communication.service.SmartAIGateway", BudgetBlockedGateway
    )
    try:
        response = client.post(
            "/api/v1/communication/sentence/generate",
            json={"sentence": "communicate a detailed unique request"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["generated_sentence"]


def test_entitlements_default_to_free_and_keep_safety_available(db):
    service = EntitlementService(db)
    assert service.get_plan(USER_ID) == Plan.FREE
    assert service.has_feature_access(USER_ID, Feature.AAC_BASIC.value)
    assert service.has_feature_access(USER_ID, Feature.AAC_EMERGENCY.value)
    assert not service.has_feature_access(USER_ID, Feature.AAC_AI_GENERATION.value)
