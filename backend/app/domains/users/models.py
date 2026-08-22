import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: f"user-{uuid.uuid4().hex[:8]}")
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="caregiver")
    created_at = Column(DateTime, default=datetime.utcnow)

    caregiver_profile = relationship("Caregiver", back_populates="user", uselist=False, cascade="all, delete-orphan")
    children = relationship("Child", back_populates="caregiver", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
