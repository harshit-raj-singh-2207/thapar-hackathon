import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class PaymentConfigurationError(RuntimeError):
    pass


class PaymentProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderVerification:
    verified: bool
    status: str


class PaymentProvider(Protocol):
    name: str
    public_key: str

    def create_checkout(self, *, amount_minor: int, currency: str, receipt: str, notes: dict) -> dict: ...
    def verify_payment(self, *, order_id: str, payment_id: str, signature: str, amount_minor: int) -> ProviderVerification: ...
    def handle_webhook(self, *, payload: bytes, signature: str) -> dict: ...
    def cancel_subscription(self, provider_subscription_id: str) -> dict: ...


class RazorpayProvider:
    name = "razorpay"
    api_base = "https://api.razorpay.com/v1"

    def __init__(self, key_id: str, key_secret: str, webhook_secret: str, timeout: float = 10):
        if not key_id or not key_secret:
            raise PaymentConfigurationError("Payment provider is not configured.")
        self.public_key = key_id
        self._key_secret = key_secret
        self._webhook_secret = webhook_secret
        self._timeout = timeout

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        auth = base64.b64encode(f"{self.public_key}:{self._key_secret}".encode()).decode()
        request = Request(
            f"{self.api_base}{path}", method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                return json.loads(response.read().decode())
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise PaymentProviderError("Payment provider request failed.") from exc

    def create_checkout(self, *, amount_minor: int, currency: str, receipt: str, notes: dict) -> dict:
        return self._request("POST", "/orders", {
            "amount": amount_minor, "currency": currency, "receipt": receipt,
            "notes": notes,
        })

    def verify_payment(self, *, order_id: str, payment_id: str, signature: str, amount_minor: int) -> ProviderVerification:
        expected = hmac.new(
            self._key_secret.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return ProviderVerification(False, "invalid_signature")
        payment = self._request("GET", f"/payments/{payment_id}")
        valid = (
            payment.get("order_id") == order_id
            and int(payment.get("amount", -1)) == amount_minor
            and payment.get("status") in {"authorized", "captured"}
        )
        return ProviderVerification(valid, str(payment.get("status", "invalid")))

    def handle_webhook(self, *, payload: bytes, signature: str) -> dict:
        if not self._webhook_secret:
            raise PaymentConfigurationError("Payment webhook is not configured.")
        expected = hmac.new(self._webhook_secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise PaymentProviderError("Invalid webhook signature.")
        try:
            return json.loads(payload.decode())
        except ValueError as exc:
            raise PaymentProviderError("Invalid webhook payload.") from exc

    def cancel_subscription(self, provider_subscription_id: str) -> dict:
        return self._request("POST", f"/subscriptions/{provider_subscription_id}/cancel", {})
