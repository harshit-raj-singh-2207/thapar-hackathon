from typing import Optional

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    plan_id: str = "PREMIUM"


class CheckoutResponse(BaseModel):
    provider: str
    order_id: str
    key_id: str
    amount: int
    currency: str
    plan_id: str


class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str


class PaymentResult(BaseModel):
    verified: bool
    status: str
    plan_id: Optional[str] = None
    message: str
