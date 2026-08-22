import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.core.database import Base

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String, primary_key=True, default=lambda: f"ticket-{uuid.uuid4().hex[:8]}")
    ticket_number = Column(String, unique=True, nullable=False, default=lambda: f"SUP-{uuid.uuid4().hex[:6].upper()}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    category = Column(String, nullable=False, default="General Inquiry")
    description = Column(String, nullable=False)
    status = Column(String, default="in_progress")  # in_progress, open, resolved
    created_at = Column(DateTime, default=datetime.utcnow)

class ScheduledSupportCall(Base):
    __tablename__ = "scheduled_support_calls"

    id = Column(String, primary_key=True, default=lambda: f"call-{uuid.uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    specialist_name = Column(String, default="Sarah J.")
    scheduled_time = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
