import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.core.database import Base


class SensoryStateRecord(Base):
    """A user-reported sensory state; no state is inferred by AI."""

    __tablename__ = "sensory_state_records"

    id = Column(
        String(64),
        primary_key=True,
        default=lambda: f"sensory-{uuid.uuid4().hex}",
    )
    user_id = Column(
        String(64),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sensory_state = Column(String(40), nullable=False, index=True)
    intensity = Column(Integer, nullable=False)
    optional_note = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
