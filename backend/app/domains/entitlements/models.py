import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String

from app.core.database import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(String(64), primary_key=True, default=lambda: f"sub-{uuid.uuid4().hex}")
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    plan = Column(String(24), nullable=False, default="FREE")
    status = Column(String(24), nullable=False, default="active", index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    # Retained for compatibility with subscriptions created before expires_at.
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


Subscription = UserSubscription
