from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.payments.provider import PaymentConfigurationError
from app.domains.payments.schemas import CheckoutRequest, CheckoutResponse, PaymentResult, VerifyPaymentRequest
from app.domains.payments.service import PaymentService
from app.models.user import User


router = APIRouter(prefix="/payments", tags=["Payments"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    try:
        return PaymentService(db)
    except PaymentConfigurationError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> CheckoutResponse:
    return service.create_checkout(current_user.id, request.plan_id)


@router.post("/verify", response_model=PaymentResult)
def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResult:
    return service.verify_payment(
        current_user.id, request.order_id, request.payment_id, request.signature
    )


@router.post("/webhook", response_model=PaymentResult)
async def payment_webhook(
    request: Request,
    payment_signature: str = Header(default="", alias="X-Payment-Signature"),
    provider_signature: str = Header(default="", alias="X-Razorpay-Signature"),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentResult:
    return service.handle_webhook(
        await request.body(), payment_signature or provider_signature
    )
