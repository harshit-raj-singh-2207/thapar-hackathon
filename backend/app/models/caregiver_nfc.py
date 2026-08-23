import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class CaregiverNFC(Base):
    __tablename__ = "caregiver_nfc_authorizations"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"cgnfc-{uuid.uuid4().hex[:8]}")
    caregiver_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    nfc_identifier = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="active", nullable=False, index=True)  # active, inactive, revoked
    last_pickup_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    caregiver = relationship("User", foreign_keys=[caregiver_id])
    child = relationship("Child", foreign_keys=[child_id])
