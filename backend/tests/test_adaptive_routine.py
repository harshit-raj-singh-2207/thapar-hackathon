from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.ai.gateway import GatewayResult
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.entitlements.models import UserSubscription
from app.main import app


client = TestClient(app)
OWNER_ID = "user-verified-sarah"
CAREGIVER_ID = "user-verified-david"


def _override(db, user_id):
    def database():
        yield db

    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=user_id, role="caregiver"
    )


def _premium(db, user_id=OWNER_ID):
    db.add(UserSubscription(user_id=user_id, plan="PREMIUM", status="active"))
    db.commit()


def _create_routine(db):
    _override(db, OWNER_ID)
    response = client.post(
        "/api/v1/learning/routines",
        json={
            "title": "Morning routine",
            "time_of_day": "morning",
            "steps": [
                {"step_number": 1, "title": "Wake up"},
                {"step_number": 2, "title": "Brush teeth"},
            ],
        },
    )
    assert response.status_code == 200
    return response.json()


def test_free_user_can_create_and_read_daily_routines(db):
    _override(db, OWNER_ID)
    try:
        created = _create_routine(db)
        response = client.get("/api/v1/learning/routines")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert any(item["id"] == created["id"] for item in response.json())


def test_free_user_can_complete_routine_task(db):
    try:
        routine = _create_routine(db)
        step_id = routine["steps"][0]["id"]
        response = client.post(f"/api/v1/learning/routines/steps/{step_id}/toggle")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["is_completed"] is True


def test_premium_adaptive_multi_day_planning_uses_gateway(db, monkeypatch):
    _premium(db)
    _override(db, OWNER_ID)

    class Gateway:
        def __init__(self, gateway_db):
            assert gateway_db is db

        def generate_text(self, **kwargs):
            assert kwargs["feature"] == "routine_adaptation"
            return GatewayResult(
                text="Use a gentle three-day transition plan.",
                source="external",
                provider="groq",
                budget_status="NORMAL",
            )

    monkeypatch.setattr(
        "app.domains.learning.adaptive_routine_service.SmartAIGateway", Gateway
    )
    try:
        response = client.post(
            "/api/v1/learning/routines/adaptive-plan",
            json={"goal": "prepare for school", "days": 3},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["source"] == "external"
    assert response.json()["days"] == 3


def test_free_user_is_denied_adaptive_planning(db):
    _override(db, OWNER_ID)
    try:
        response = client.post(
            "/api/v1/learning/routines/adaptive-plan",
            json={"goal": "prepare for school", "days": 2},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "premium_feature_required"


def test_adaptive_ai_budget_failure_returns_local_fallback(db, monkeypatch):
    _premium(db)
    _override(db, OWNER_ID)

    class BlockedGateway:
        def __init__(self, gateway_db):
            assert gateway_db is db

        def generate_text(self, **kwargs):
            return GatewayResult(
                text=kwargs["fallback"](),
                source="local_fallback",
                provider="local",
                budget_status="BLOCK_OPTIONAL_APIS",
                fallback_reason="budget_denied",
            )

    monkeypatch.setattr(
        "app.domains.learning.adaptive_routine_service.SmartAIGateway", BlockedGateway
    )
    try:
        response = client.post(
            "/api/v1/learning/routines/adaptive-plan",
            json={"goal": "handle a schedule change", "days": 1},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["source"] == "local_fallback"
    assert response.json()["suggested_steps"]


def test_premium_owner_can_share_editing_with_caregiver(db):
    _premium(db)
    try:
        routine = _create_routine(db)
        share = client.post(
            f"/api/v1/learning/routines/{routine['id']}/share",
            json={"caregiver_user_id": CAREGIVER_ID, "can_edit": True},
        )
        assert share.status_code == 200

        _override(db, CAREGIVER_ID)
        step_id = routine["steps"][0]["id"]
        toggled = client.post(
            f"/api/v1/learning/routines/steps/{step_id}/toggle"
        )
    finally:
        app.dependency_overrides.clear()
    assert toggled.status_code == 200
    assert toggled.json()["is_completed"] is True
