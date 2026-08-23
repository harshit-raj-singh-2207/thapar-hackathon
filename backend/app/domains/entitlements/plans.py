from app.core.config import settings
from app.domains.entitlements.plan_schemas import PlanResponse
from app.domains.entitlements.service import Feature, PLAN_FEATURES, Plan


PLAN_PRESENTATION = {
    Plan.FREE: {
        "name": "Free",
        "billing_period": "forever",
        "description": "Essential communication, sensory, routine, and safety support.",
        "highlighted_features": [
            Feature.AAC_BASIC.value,
            Feature.AAC_EMERGENCY.value,
            Feature.SENSORY_BASIC.value,
            Feature.ROUTINE_BASIC.value,
            Feature.SAFETY_CORE.value,
            Feature.SAFETY_STATUS.value,
        ],
        "recommended": False,
    },
    Plan.PREMIUM: {
        "name": "Premium",
        "billing_period": "monthly",
        "description": "Personalization, adaptive support, history, and caregiver insights.",
        "highlighted_features": [
            Feature.AAC_AI_GENERATION.value,
            Feature.SENSORY_ANALYTICS.value,
            Feature.ROUTINE_ADAPTIVE.value,
            Feature.SAFETY_MULTIPLE_SAFE_ZONES.value,
            Feature.CAREGIVER_INTELLIGENCE.value,
        ],
        "recommended": True,
    },
    Plan.INSTITUTION: {
        "name": "Institution",
        "billing_period": "contact_sales",
        "description": "Organization, staff, and aggregate capabilities for care and education teams.",
        "highlighted_features": [
            Feature.INSTITUTION_ORGANIZATION.value,
            Feature.INSTITUTION_STAFF.value,
            Feature.INSTITUTION_AGGREGATE_ANALYTICS.value,
        ],
        "recommended": False,
    },
}


def get_plan_catalog(settings_obj=settings) -> list[PlanResponse]:
    """Build public plan metadata from the authoritative entitlement map."""
    prices = {
        Plan.FREE: 0.0,
        Plan.PREMIUM: float(settings_obj.PREMIUM_MONTHLY_PRICE_INR),
        Plan.INSTITUTION: None,
    }
    return [
        PlanResponse(
            plan_id=plan.value,
            price=prices[plan],
            currency="INR",
            included_features=sorted(PLAN_FEATURES[plan]),
            **PLAN_PRESENTATION[plan],
        )
        for plan in (Plan.FREE, Plan.PREMIUM, Plan.INSTITUTION)
    ]
