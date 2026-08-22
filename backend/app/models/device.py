import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Device(Base):
    __tablename__ = "devices"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"dev-{uuid.uuid4().hex[:8]}")
    child_id = Column(String, ForeignKey("children.id"), nullable=True, index=True)
    device_name = Column(String, nullable=False, default="GPS Safety Band")
    device_type = Column(String, default="gps_band")  # gps_band, smartwatch, pendant, smartphone
    serial_number = Column(String, unique=True, index=True, nullable=False)
    device_identifier = Column(String, nullable=True, index=True)
    battery_level = Column(Integer, default=100)  # 0 - 100 percentage
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=True)
    connection_status = Column(String, default="online")  # online, offline, standby
    gps_status = Column(String, default="active")  # active, standby, searching, offline
    firmware_version = Column(String, default="v1.2.0")
    last_ping_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    child = relationship("Child", back_populates="devices")
    locations = relationship("Location", back_populates="device", cascade="all, delete-orphan")
