from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.domains.entitlements.plans import get_plan_catalog
from app.domains.entitlements.service import Feature, PLAN_FEATURES, Plan
from app.main import app


client = TestClient(app)


def _plans_by_id():
    response = client.get("/api/v1/plans")
    assert response.status_code == 200
    return {plan["plan_id"]: plan for plan in response.json()}


def test_plans_endpoint_returns_all_supported_plans():
    plans = _plans_by_id()
    assert set(plans) == {"FREE", "PREMIUM", "INSTITUTION"}


def test_free_plan_contains_critical_accessibility_and_safety_features():
    free = _plans_by_id()["FREE"]
    assert free["price"] == 0
    assert free["billing_period"] == "forever"
    assert Feature.AAC_EMERGENCY.value in free["included_features"]
    assert Feature.SENSORY_BASIC.value in free["included_features"]
    assert Feature.ROUTINE_BASIC.value in free["included_features"]
    assert Feature.SAFETY_CORE.value in free["included_features"]
    assert Feature.SAFETY_STATUS.value in free["included_features"]


def test_premium_plan_is_returned_with_monthly_pricing():
    premium = _plans_by_id()["PREMIUM"]
    assert premium["currency"] == "INR"
    assert premium["billing_period"] == "monthly"
    assert premium["price"] >= 0
    assert premium["recommended"] is True
    assert Feature.AAC_AI_GENERATION.value in premium["included_features"]


def test_institution_plan_uses_contact_sales():
    institution = _plans_by_id()["INSTITUTION"]
    assert institution["price"] is None
    assert institution["billing_period"] == "contact_sales"
    assert Feature.INSTITUTION_STAFF.value in institution["included_features"]


def test_catalog_feature_mapping_matches_authoritative_entitlements():
    for item in get_plan_catalog():
        plan = Plan(item.plan_id)
        assert set(item.included_features) == PLAN_FEATURES[plan]
        assert set(item.highlighted_features).issubset(set(item.included_features))


def test_premium_price_uses_configuration():
    catalog = get_plan_catalog(SimpleNamespace(PREMIUM_MONTHLY_PRICE_INR=749.5))
    premium = next(item for item in catalog if item.plan_id == "PREMIUM")
    assert premium.price == 749.5
