import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class Child(Base):
    __tablename__ = "children"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"child-{uuid.uuid4().hex[:8]}")
    caregiver_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    autism_level = Column(String, nullable=True, default="Level 1")  # Level 1, Level 2, Level 3
    medical_notes = Column(Text, nullable=True)
    tracking_enabled = Column(Boolean, default=True)
    current_status = Column(String, default="safe")  # safe, out_of_bounds, separation_alert, emergency
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    caregiver = relationship("User", back_populates="children")
    devices = relationship("Device", back_populates="child", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="child", cascade="all, delete-orphan")
    safe_zones = relationship("SafeZone", back_populates="child", cascade="all, delete-orphan")
    emergencies = relationship("EmergencyAlert", back_populates="child", cascade="all, delete-orphan")
    safety_events = relationship("SafetyEvent", back_populates="child", cascade="all, delete-orphan")
