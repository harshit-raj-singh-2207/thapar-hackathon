import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config.database import Base

class SafeZone(Base):
    __tablename__ = "safe_zones"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"sz-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id"), nullable=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Home", "School", "Sensory Therapy Clinic", "School Gate"
    nfc_tag_id = Column(String, unique=True, index=True, nullable=True)  # Physical NFC Checkpoint Tag ID
    status = Column(String, default="active", nullable=True, index=True)  # active, inactive, maintenance
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

    @property
    def checkpoint_id(self) -> str:
        return self.id

    @property
    def latitude(self) -> float:
        return self.center_latitude

    @latitude.setter
    def latitude(self, val: float):
        self.center_latitude = val

    @property
    def longitude(self) -> float:
        return self.center_longitude

    @longitude.setter
    def longitude(self, val: float):
        self.center_longitude = val

    @property
    def radius(self) -> float:
        return self.radius_meters

    @radius.setter
    def radius(self, val: float):
        self.radius_meters = val
