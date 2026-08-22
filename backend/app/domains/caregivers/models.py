import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.core.database import Base

from sqlalchemy.orm import relationship

class Caregiver(Base):
    __tablename__ = "caregivers"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"cg-{uuid.uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(String, nullable=True, default="Parent caregiver")
    avatar_url = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="caregiver_profile")

class CaregiverBlock(Base):
    __tablename__ = "caregiver_blocks"

    id = Column(String, primary_key=True, default=lambda: f"block-{uuid.uuid4().hex[:8]}")
    blocker_id = Column(String, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ContentReport(Base):
    __tablename__ = "content_reports"

    id = Column(String, primary_key=True, default=lambda: f"report-{uuid.uuid4().hex[:8]}")
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_type = Column(String, nullable=False)  # post, comment, user
    target_id = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class CaregiverPrivacySettings(Base):
    __tablename__ = "caregiver_privacy_settings"

    id = Column(String, primary_key=True, default=lambda: f"priv-{uuid.uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    profile_visibility = Column(String, default="Public")
    messaging_privacy = Column(String, default="Connections Only")
    group_privacy = Column(String, default="Active")
    notification_privacy = Column(String, default="All Alerts")
    
    # Granular Privacy Toggles matching UI
    public_profile = Column(Boolean, default=False)
    show_location = Column(Boolean, default=True)
    activity_status = Column(Boolean, default=True)
    receive_direct_messages = Column(Boolean, default=True)
    filter_unknown_senders = Column(Boolean, default=True)
    read_receipts = Column(Boolean, default=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationSubmission(Base):
    __tablename__ = "verification_submissions"

    id = Column(String, primary_key=True, default=lambda: f"verif-{uuid.uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role_bio = Column(String, nullable=True)
    document_notes = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, verified, rejected
    submitted_at = Column(DateTime, default=datetime.utcnow)


