import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class SafeZone(Base):
    __tablename__ = "safe_zones"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"sz-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "Home", "School", "Sensory Therapy Clinic"
    zone_type = Column(String, default="circle")  # circle, polygon
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, default=150.0)  # used for circular zones
    polygon_coordinates = Column(Text, nullable=True)  # JSON string of [(lat, lon), ...]
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    alert_on_exit = Column(Boolean, default=True)
    alert_on_enter = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    child = relationship("Child", back_populates="safe_zones")
