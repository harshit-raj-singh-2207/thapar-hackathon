from typing import Literal, Optional

from pydantic import BaseModel, Field


class PlanResponse(BaseModel):
    plan_id: str
    name: str
    price: Optional[float] = Field(default=None, ge=0)
    currency: str
    billing_period: Literal["forever", "monthly", "contact_sales"]
    description: str
    included_features: list[str]
    highlighted_features: list[str]
    recommended: bool = False
