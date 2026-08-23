import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship, validates
from app.config.database import Base

VALID_EMERGENCY_STATUSES = {"scheduled", "active", "expired", "inactive"}

class EmergencyMode(Base):
    __tablename__ = "emergency_modes"
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'active', 'expired', 'inactive')",
            name="check_valid_emergency_status",
        ),
        Index("idx_emergency_mode_child_status", "child_id", "status"),
        {"extend_existing": True},
    )

    id = Column(String, primary_key=True, default=lambda: f"emg-mode-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    caregiver_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="active", nullable=False, index=True)  # scheduled, active, expired, inactive
    emergency_type = Column(String, default="pandemic_lockdown", nullable=False)
    reason = Column(Text, default="Worldwide Pandemic Emergency - Physical Gathering Restrictions", nullable=False)
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration_days = Column(Integer, default=90, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    child = relationship("Child", back_populates="emergency_mode")
    caregiver = relationship("User", backref="emergency_modes")
    preferences = relationship(
        "EmergencySupportPreferences",
        back_populates="emergency_mode",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @validates("status")
    def validate_status(self, key, value):
        if value not in VALID_EMERGENCY_STATUSES:
            raise ValueError(f"Invalid status '{value}'. Must be one of {VALID_EMERGENCY_STATUSES}")
        return value

    @property
    def effective_status(self) -> str:
        """Dynamically computes the active/expired/scheduled state based on current UTC time."""
        if self.status == "inactive" or not self.is_active:
            return "inactive"
        now = datetime.now(timezone.utc)
        start = self.start_date.replace(tzinfo=timezone.utc) if self.start_date.tzinfo is None else self.start_date
        end = self.end_date.replace(tzinfo=timezone.utc) if self.end_date.tzinfo is None else self.end_date

        if now < start:
            return "scheduled"
        elif now >= end:
            return "expired"
        return "active"

    @property
    def days_remaining(self) -> int:
        """Calculates days remaining if currently active."""
        if self.effective_status != "active":
            return 0
        now = datetime.now(timezone.utc)
        end = self.end_date.replace(tzinfo=timezone.utc) if self.end_date.tzinfo is None else self.end_date
        return max(0, (end - now).days)


class EmergencySupportPreferences(Base):
    __tablename__ = "emergency_support_preferences"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"emg-pref-{uuid.uuid4().hex[:8]}")
    emergency_mode_id = Column(
        String,
        ForeignKey("emergency_modes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    communication_enabled = Column(Boolean, default=True, nullable=False)
    learning_enabled = Column(Boolean, default=True, nullable=False)
    emotion_support_enabled = Column(Boolean, default=True, nullable=False)
    emotional_support_enabled = Column(Boolean, default=True, nullable=True)
    games_enabled = Column(Boolean, default=True, nullable=False)
    safety_monitoring_enabled = Column(Boolean, default=True, nullable=False)
    caregiver_notifications_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    emergency_mode = relationship("EmergencyMode", back_populates="preferences")

    def __init__(self, **kwargs):
        if "emotion_support_enabled" in kwargs and "emotional_support_enabled" not in kwargs:
            kwargs["emotional_support_enabled"] = kwargs["emotion_support_enabled"]
        elif "emotional_support_enabled" in kwargs and "emotion_support_enabled" not in kwargs:
            kwargs["emotion_support_enabled"] = kwargs["emotional_support_enabled"]
        super().__init__(**kwargs)

