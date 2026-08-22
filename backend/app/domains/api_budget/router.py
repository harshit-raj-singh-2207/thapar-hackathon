from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.api_budget.schemas import (
    APIUsageHistoryResponse,
    BudgetSummaryResponse,
    UsageBreakdownItem,
    UsageBreakdownResponse,
)
from app.domains.api_budget.service import APIBudgetService
from app.domains.users.models import User


router = APIRouter(prefix="/api-budget", tags=["API Budget"])


@router.get("/summary", response_model=BudgetSummaryResponse)
def get_budget_summary(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return APIBudgetService(db).get_summary(month)


def _breakdown_response(service: APIBudgetService, month: str, values) -> UsageBreakdownResponse:
    return UsageBreakdownResponse(
        month=month,
        items=[UsageBreakdownItem(name=name, **details) for name, details in values.items()],
    )


@router.get("/providers", response_model=UsageBreakdownResponse)
def get_provider_usage(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = APIBudgetService(db)
    selected_month = month or service.current_month()
    return _breakdown_response(service, selected_month, service.get_provider_usage(selected_month))


@router.get("/features", response_model=UsageBreakdownResponse)
def get_feature_usage(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = APIBudgetService(db)
    selected_month = month or service.current_month()
    return _breakdown_response(service, selected_month, service.get_feature_usage(selected_month))


@router.get("/history", response_model=APIUsageHistoryResponse)
def get_usage_history(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    provider: Optional[str] = Query(None, max_length=80),
    feature: Optional[str] = Query(None, max_length=120),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = APIBudgetService(db)
    selected_month = month or service.current_month()
    items, total = service.repo.history(selected_month, page, page_size, provider, feature)
    return APIUsageHistoryResponse(
        month=selected_month,
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )
