import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(String(64), primary_key=True, default=lambda: f"pay-{uuid.uuid4().hex}")
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(32), nullable=False, index=True)
    provider_order_id = Column(String(128), nullable=False, unique=True, index=True)
    provider_payment_id = Column(String(128), nullable=True, unique=True, index=True)
    plan = Column(String(24), nullable=False)
    amount_minor = Column(Integer, nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    status = Column(String(24), nullable=False, default="created", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
