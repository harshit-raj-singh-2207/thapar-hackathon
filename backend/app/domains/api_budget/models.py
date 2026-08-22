import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Numeric, String

from app.core.database import Base


class APIUsageRecord(Base):
    __tablename__ = "api_usage_records"

    id = Column(String(64), primary_key=True, default=lambda: f"usage-{uuid.uuid4().hex}")
    provider = Column(String(80), nullable=False, index=True)
    feature = Column(String(120), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False)
    user_id = Column(String(64), nullable=True, index=True)
    estimated_cost = Column(Numeric(12, 4), nullable=False, default=0)
    request_count = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    month = Column(String(7), nullable=False, index=True)  # YYYY-MM
    status = Column(String(40), nullable=False, default="success", index=True)
