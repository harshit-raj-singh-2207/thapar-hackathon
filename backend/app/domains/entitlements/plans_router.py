from fastapi import APIRouter

from app.domains.entitlements.plan_schemas import PlanResponse
from app.domains.entitlements.plans import get_plan_catalog


router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("", response_model=list[PlanResponse], summary="List NIVARA product plans")
def list_plans() -> list[PlanResponse]:
    return get_plan_catalog()
