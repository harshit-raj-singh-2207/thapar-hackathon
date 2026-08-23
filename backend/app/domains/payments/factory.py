from app.core.config import settings
from app.domains.payments.provider import PaymentConfigurationError, RazorpayProvider


def get_payment_provider(settings_obj=settings):
    provider = str(settings_obj.PAYMENT_PROVIDER).strip().lower()
    if provider != "razorpay":
        raise PaymentConfigurationError("Unsupported payment provider configuration.")
    return RazorpayProvider(
        key_id=settings_obj.PAYMENT_KEY_ID,
        key_secret=settings_obj.PAYMENT_KEY_SECRET,
        webhook_secret=settings_obj.PAYMENT_WEBHOOK_SECRET,
        timeout=settings_obj.PAYMENT_REQUEST_TIMEOUT_SECONDS,
    )
