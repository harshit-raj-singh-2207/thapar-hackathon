import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.config.database import Base

class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (
        Index("idx_child_created_at", "child_id", "created_at"),
        {"extend_existing": True}
    )

    id = Column(String, primary_key=True, default=lambda: f"loc-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, default=5.0)  # meters
    altitude = Column(Float, nullable=True)  # meters
    speed = Column(Float, default=0.0)  # m/s or km/h
    heading = Column(Float, default=0.0)  # 0 - 360 degrees
    battery_level = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    source = Column(String, nullable=True, default="gps")  # gps, network, device, manual
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    child = relationship("Child", back_populates="locations")
    device = relationship("Device", back_populates="locations")
