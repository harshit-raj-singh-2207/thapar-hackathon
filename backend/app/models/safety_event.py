import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class SafetyEvent(Base):
    __tablename__ = "safety_events"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"event-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # geofence_exit, geofence_entry, separation_alert, low_battery, device_offline, sos_triggered, speed_alert
    severity = Column(String, default="warning")  # info, warning, critical
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON string of event payload
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    child = relationship("Child", back_populates="safety_events")
