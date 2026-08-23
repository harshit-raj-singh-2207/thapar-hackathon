from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.api_budget.models import APIUsageRecord
from app.domains.api_budget.repository import APIBudgetRepository


class APIBudgetService:
    """Tracks external API spend and guards optional paid calls."""

    SAFETY_BYPASS_FEATURES = frozenset({"explicit_sos", "sos", "emergency_sos"})
    CHARGEABLE_STATUSES = frozenset({"success", "completed", "bypassed_for_safety"})

    def __init__(self, db: Session, monthly_budget: Optional[Decimal] = None):
        self.db = db
        self.repo = APIBudgetRepository(db)
        self.monthly_budget = self._money(
            monthly_budget if monthly_budget is not None else settings.MONTHLY_API_BUDGET_INR
        )
        if self.monthly_budget <= 0:
            raise ValueError("Monthly API budget must be greater than zero.")

    @staticmethod
    def current_month(at: Optional[datetime] = None) -> str:
        return (at or datetime.utcnow()).strftime("%Y-%m")

    @staticmethod
    def _money(value) -> Decimal:
        try:
            return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("Cost must be a valid numeric amount.") from exc

    @classmethod
    def is_safety_bypass(cls, feature: str) -> bool:
        return feature.strip().lower() in cls.SAFETY_BYPASS_FEATURES

    def get_monthly_usage(self, month: Optional[str] = None) -> Decimal:
        return self.repo.monthly_usage(month or self.current_month())

    def get_remaining_budget(self, month: Optional[str] = None) -> Decimal:
        remaining = self.monthly_budget - self.get_monthly_usage(month)
        return max(Decimal("0"), remaining)

    def get_budget_percentage(self, month: Optional[str] = None) -> float:
        used = self.get_monthly_usage(month)
        return round(float((used / self.monthly_budget) * Decimal("100")), 2)

    def get_budget_status(self, month: Optional[str] = None) -> str:
        percentage = self.get_budget_percentage(month)
        if percentage >= 100:
            return "BLOCK_OPTIONAL_APIS"
        if percentage >= 95:
            return "EMERGENCY"
        if percentage >= 85:
            return "RESTRICTED"
        if percentage >= 70:
            return "WARNING"
        return "NORMAL"

    def can_use_api(
        self,
        provider: str,
        feature: str,
        estimated_cost,
        month: Optional[str] = None,
    ) -> bool:
        del provider  # Reserved for future provider-specific limits.
        if self.is_safety_bypass(feature):
            return True
        cost = self._money(estimated_cost)
        if cost < 0:
            raise ValueError("Estimated cost cannot be negative.")
        used = self.get_monthly_usage(month)
        return used < self.monthly_budget and used + cost <= self.monthly_budget

    def record_api_usage(
        self,
        provider: str,
        feature: str,
        endpoint: str,
        estimated_cost,
        user_id: Optional[str] = None,
        request_count: int = 1,
        status: str = "success",
        timestamp: Optional[datetime] = None,
    ) -> APIUsageRecord:
        if not provider.strip() or not feature.strip() or not endpoint.strip():
            raise ValueError("Provider, feature, and endpoint are required.")
        if request_count < 1:
            raise ValueError("Request count must be at least one.")
        cost = self._money(estimated_cost)
        if cost < 0:
            raise ValueError("Estimated cost cannot be negative.")
        occurred_at = timestamp or datetime.utcnow()
        # Failed and budget-blocked requests are auditable but do not consume budget.
        charge = cost if status.strip().lower() in self.CHARGEABLE_STATUSES else Decimal("0")
        record = APIUsageRecord(
            provider=provider.strip().lower(),
            feature=feature.strip().lower(),
            endpoint=endpoint.strip(),
            user_id=user_id,
            estimated_cost=charge,
            request_count=request_count,
            timestamp=occurred_at,
            month=self.current_month(occurred_at),
            status=status.strip().lower(),
        )
        return self.repo.create(record)

    def get_provider_usage(self, month: Optional[str] = None) -> Dict[str, Dict[str, object]]:
        return self._breakdown(self.repo.grouped_usage(month or self.current_month(), APIUsageRecord.provider))

    def get_feature_usage(self, month: Optional[str] = None) -> Dict[str, Dict[str, object]]:
        return self._breakdown(self.repo.grouped_usage(month or self.current_month(), APIUsageRecord.feature))

    def _breakdown(self, rows) -> Dict[str, Dict[str, object]]:
        return {
            name: {
                "estimated_cost": cost,
                "request_count": count,
                "percentage_of_budget": round(float((cost / self.monthly_budget) * Decimal("100")), 2),
            }
            for name, cost, count in rows
        }

    def get_summary(self, month: Optional[str] = None) -> Dict[str, object]:
        selected_month = month or self.current_month()
        used = self.get_monthly_usage(selected_month)
        return {
            "monthly_budget": self.monthly_budget,
            "used": used,
            "remaining": max(Decimal("0"), self.monthly_budget - used),
            "percentage": round(float((used / self.monthly_budget) * Decimal("100")), 2),
            "status": self.get_budget_status(selected_month),
            "month": selected_month,
        }
