from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BudgetSummaryResponse(BaseModel):
    monthly_budget: float
    used: float
    remaining: float
    percentage: float
    status: str
    month: str


class UsageBreakdownItem(BaseModel):
    name: str
    estimated_cost: float
    request_count: int
    percentage_of_budget: float


class UsageBreakdownResponse(BaseModel):
    month: str
    items: List[UsageBreakdownItem]


class APIUsageHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider: str
    feature: str
    endpoint: str
    user_id: Optional[str]
    estimated_cost: float
    request_count: int
    timestamp: datetime
    month: str
    status: str


class APIUsageHistoryResponse(BaseModel):
    month: str
    total: int
    page: int
    page_size: int
    items: List[APIUsageHistoryItem]
