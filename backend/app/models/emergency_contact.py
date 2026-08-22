import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"contact-{uuid.uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    child_id = Column(String, ForeignKey("children.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    relationship_type = Column(String, default="Family")  # Mother, Father, Grandparent, Doctor, Police
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    priority_order = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    notify_via_sms = Column(Boolean, default=True)
    notify_via_call = Column(Boolean, default=True)
    notify_via_push = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="emergency_contacts")
