from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.domains.api_budget.models import APIUsageRecord
from app.domains.api_budget.service import APIBudgetService


def record_cost(service: APIBudgetService, amount: str, feature: str = "ai_communication"):
    return service.record_api_usage(
        provider="groq",
        feature=feature,
        endpoint="https://api.example.test/v1/chat",
        estimated_cost=Decimal(amount),
        user_id="user-verified-sarah",
    )


def test_normal_usage(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "600")
    assert service.get_monthly_usage() == Decimal("600.0000")
    assert service.get_remaining_budget() == Decimal("900.0000")
    assert service.get_budget_percentage() == 40.0
    assert service.get_budget_status() == "NORMAL"


def test_warning_threshold(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "1050")
    assert service.get_budget_status() == "WARNING"


def test_restricted_threshold(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "1275")
    assert service.get_budget_status() == "RESTRICTED"


def test_emergency_threshold(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "1425")
    assert service.get_budget_status() == "EMERGENCY"


def test_budget_exceeded_blocks_optional_apis(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "1500")
    assert service.get_budget_status() == "BLOCK_OPTIONAL_APIS"
    assert service.can_use_api("openai", "ai_communication", Decimal("0.10")) is False


def test_projected_cost_cannot_cross_budget(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "1499.95")
    assert service.can_use_api("openai", "ai_communication", Decimal("0.06")) is False


def test_safety_feature_bypass(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "1600")
    assert service.get_budget_status() == "BLOCK_OPTIONAL_APIS"
    assert service.can_use_api("notification_service", "explicit_sos", Decimal("25")) is True


def test_failed_or_blocked_call_is_audited_without_cost(db):
    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    service.record_api_usage(
        provider="openai",
        feature="ai_communication",
        endpoint="https://api.example.test/v1/chat",
        estimated_cost="5",
        status="blocked_budget",
    )
    assert service.get_monthly_usage() == Decimal("0.0000")
    assert db.query(APIUsageRecord).count() == 1


def test_budget_endpoints_are_authenticated_and_return_aggregates(db):
    client = TestClient(app)
    assert client.get("/api/v1/api-budget/summary").status_code == 401

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "sarah@nivara.app", "password": "password123"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    service = APIBudgetService(db, monthly_budget=Decimal("1500"))
    record_cost(service, "120")

    summary = client.get("/api/v1/api-budget/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["used"] == 120.0
    assert summary.json()["status"] == "NORMAL"

    providers = client.get("/api/v1/api-budget/providers", headers=headers)
    assert providers.status_code == 200
    assert providers.json()["items"][0]["name"] == "groq"

    features = client.get("/api/v1/api-budget/features", headers=headers)
    assert features.status_code == 200
    assert features.json()["items"][0]["name"] == "ai_communication"

    history = client.get("/api/v1/api-budget/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] == 1
