import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"emg-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    caregiver_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="active")  # active, resolved, false_alarm
    severity = Column(String, default="critical")  # critical, high, medium
    triggered_by = Column(String, default="sos_button")  # sos_button, geofence_breach, separation, caregiver_app
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    child = relationship("Child", back_populates="emergencies")
