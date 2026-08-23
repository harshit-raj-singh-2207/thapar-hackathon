from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.entitlements.models import UserSubscription
from app.domains.entitlements.service import Plan
from app.domains.payments.factory import get_payment_provider
from app.domains.payments.models import PaymentTransaction
from app.domains.payments.provider import PaymentConfigurationError, PaymentProviderError
from app.domains.payments.schemas import CheckoutResponse, PaymentResult


class PaymentService:
    """Provider-neutral purchase orchestration and subscription activation."""

    def __init__(self, db: Session, provider=None, settings_obj=settings):
        self.db = db
        self.settings = settings_obj
        self.provider = provider if provider is not None else get_payment_provider(settings_obj)

    @staticmethod
    def _provider_failure(exc: Exception):
        code = status.HTTP_503_SERVICE_UNAVAILABLE if isinstance(exc, PaymentConfigurationError) else status.HTTP_502_BAD_GATEWAY
        raise HTTPException(status_code=code, detail=str(exc))

    def create_checkout(self, user_id: str, plan_id: str) -> CheckoutResponse:
        if str(plan_id).upper() != Plan.PREMIUM.value:
            raise HTTPException(status_code=400, detail="Only PREMIUM checkout is currently supported.")
        amount_minor = int(round(float(self.settings.PREMIUM_MONTHLY_PRICE_INR) * 100))
        if amount_minor <= 0:
            raise HTTPException(status_code=503, detail="Premium pricing is not configured safely.")
        receipt = f"nivara-{user_id[:20]}-{int(datetime.now(timezone.utc).timestamp())}"
        try:
            checkout = self.provider.create_checkout(
                amount_minor=amount_minor,
                currency="INR",
                receipt=receipt,
                notes={"user_id": user_id, "plan": Plan.PREMIUM.value},
            )
        except (PaymentConfigurationError, PaymentProviderError) as exc:
            self._provider_failure(exc)
        order_id = str(checkout.get("id") or "")
        if not order_id:
            raise HTTPException(status_code=502, detail="Payment provider returned an invalid checkout.")
        transaction = PaymentTransaction(
            user_id=user_id,
            provider=self.provider.name,
            provider_order_id=order_id,
            plan=Plan.PREMIUM.value,
            amount_minor=amount_minor,
            currency="INR",
            status="created",
        )
        self.db.add(transaction)
        self.db.commit()
        return CheckoutResponse(
            provider=self.provider.name,
            order_id=order_id,
            key_id=self.provider.public_key,
            amount=amount_minor,
            currency="INR",
            plan_id=Plan.PREMIUM.value,
        )

    def _activate(self, transaction: PaymentTransaction, payment_id: str) -> PaymentResult:
        if transaction.status == "verified":
            return PaymentResult(
                verified=True, status="verified", plan_id=transaction.plan,
                message="Payment was already processed.",
            )
        now = datetime.now(timezone.utc)
        subscription = self.db.query(UserSubscription).filter(
            UserSubscription.user_id == transaction.user_id
        ).first()
        if subscription is None:
            subscription = UserSubscription(user_id=transaction.user_id)
            self.db.add(subscription)
        existing_end = subscription.expires_at
        if existing_end is not None and existing_end.tzinfo is None:
            existing_end = existing_end.replace(tzinfo=timezone.utc)
        period_start = existing_end if existing_end and existing_end > now else now
        subscription.plan = Plan.PREMIUM.value
        subscription.status = "ACTIVE"
        subscription.started_at = subscription.started_at or now
        subscription.expires_at = period_start + timedelta(days=30)
        subscription.current_period_end = subscription.expires_at
        subscription.cancelled_at = None
        transaction.provider_payment_id = payment_id
        transaction.status = "verified"
        transaction.verified_at = now
        self.db.commit()
        return PaymentResult(
            verified=True, status="verified", plan_id=Plan.PREMIUM.value,
            message="Premium subscription activated.",
        )

    def verify_payment(self, user_id: str, order_id: str, payment_id: str, signature: str) -> PaymentResult:
        transaction = self.db.query(PaymentTransaction).filter(
            PaymentTransaction.provider_order_id == order_id,
            PaymentTransaction.user_id == user_id,
        ).first()
        if transaction is None:
            raise HTTPException(status_code=404, detail="Payment order not found.")
        if transaction.status == "verified":
            return self._activate(transaction, transaction.provider_payment_id or payment_id)
        try:
            result = self.provider.verify_payment(
                order_id=order_id, payment_id=payment_id, signature=signature,
                amount_minor=transaction.amount_minor,
            )
        except (PaymentConfigurationError, PaymentProviderError) as exc:
            self._provider_failure(exc)
        if not result.verified:
            transaction.status = "failed"
            self.db.commit()
            return PaymentResult(
                verified=False, status=result.status, plan_id=None,
                message="Payment verification failed.",
            )
        return self._activate(transaction, payment_id)

    def handle_webhook(self, payload: bytes, signature: str) -> PaymentResult:
        try:
            event = self.provider.handle_webhook(payload=payload, signature=signature)
        except (PaymentConfigurationError, PaymentProviderError) as exc:
            self._provider_failure(exc)
        payment = (((event.get("payload") or {}).get("payment") or {}).get("entity") or {})
        order_id = str(payment.get("order_id") or "")
        payment_id = str(payment.get("id") or "")
        transaction = self.db.query(PaymentTransaction).filter(
            PaymentTransaction.provider_order_id == order_id
        ).first()
        if transaction is None:
            return PaymentResult(verified=False, status="ignored", message="Unknown payment event.")
        if event.get("event") != "payment.captured" or int(payment.get("amount", -1)) != transaction.amount_minor:
            return PaymentResult(verified=False, status="ignored", message="Non-success payment event ignored.")
        return self._activate(transaction, payment_id)

    def cancel_subscription(self, provider_subscription_id: str) -> dict:
        try:
            return self.provider.cancel_subscription(provider_subscription_id)
        except (PaymentConfigurationError, PaymentProviderError) as exc:
            self._provider_failure(exc)
