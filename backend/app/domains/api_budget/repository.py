from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domains.api_budget.models import APIUsageRecord


class APIBudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: APIUsageRecord) -> APIUsageRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def monthly_usage(self, month: str) -> Decimal:
        value = (
            self.db.query(func.coalesce(func.sum(APIUsageRecord.estimated_cost), 0))
            .filter(APIUsageRecord.month == month)
            .scalar()
        )
        return Decimal(str(value or 0))

    def grouped_usage(self, month: str, field) -> List[Tuple[str, Decimal, int]]:
        rows = (
            self.db.query(
                field,
                func.coalesce(func.sum(APIUsageRecord.estimated_cost), 0),
                func.coalesce(func.sum(APIUsageRecord.request_count), 0),
            )
            .filter(APIUsageRecord.month == month)
            .group_by(field)
            .order_by(func.sum(APIUsageRecord.estimated_cost).desc())
            .all()
        )
        return [(name, Decimal(str(cost or 0)), int(count or 0)) for name, cost, count in rows]

    def history(
        self,
        month: str,
        page: int,
        page_size: int,
        provider: Optional[str] = None,
        feature: Optional[str] = None,
    ) -> Tuple[List[APIUsageRecord], int]:
        query = self.db.query(APIUsageRecord).filter(APIUsageRecord.month == month)
        if provider:
            query = query.filter(APIUsageRecord.provider == provider)
        if feature:
            query = query.filter(APIUsageRecord.feature == feature)
        total = query.count()
        items = (
            query.order_by(APIUsageRecord.timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
