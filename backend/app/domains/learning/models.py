import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Routine(Base):
    __tablename__ = "routines"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=True)
    title = Column(String(150), nullable=False)
    time_of_day = Column(String(50), default="morning")  # morning, afternoon, evening, bedtime, anytime
    icon = Column(String(50), default="🌅")
    color = Column(String(50), default="#3B82F6")
    is_active = Column(Boolean, default=True)
    streak_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    steps = relationship("RoutineStep", back_populates="routine_rel", cascade="all, delete-orphan")

class RoutineStep(Base):
    __tablename__ = "routine_steps"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    routine_id = Column(String(64), ForeignKey("routines.id"), nullable=False)
    step_number = Column(Integer, default=1)
    title = Column(String(150), nullable=False)
    instruction = Column(Text, nullable=True)
    icon = Column(String(50), default="✓")
    duration_sec = Column(Integer, default=60)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    routine_rel = relationship("Routine", back_populates="steps")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Daily Living")
    icon = Column(String(50), default="📋")
    is_completed = Column(Boolean, default=False)
    steps_data = Column(JSON, default=list)  # list of micro steps with check status
    created_at = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=True)
    title = Column(String(150), nullable=False)
    time_str = Column(String(20), nullable=False)  # e.g., "08:30 AM"
    frequency = Column(String(50), default="Daily")  # Daily, Weekdays, Once
    category = Column(String(50), default="Hydration")  # Hydration, Medication, Sensory Break, Routine
    icon = Column(String(50), default="⏰")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TutorChatSession(Base):
    __tablename__ = "tutor_chat_sessions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), nullable=True)
    topic = Column(String(100), default="General Learning")
    messages = Column(JSON, default=list)  # list of {sender: 'child'|'tutor', text: '...', timestamp: '...'}
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningTopic(Base):
    __tablename__ = "learning_topics"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(150), nullable=False)
    category = Column(String(100), default="Social Stories")  # Social Stories, Emotions, Daily Skills, Science
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="📖")
    color = Column(String(50), default="#10B981")
    modules = Column(JSON, default=list)  # list of cards / interactive story steps
    is_completed = Column(Boolean, default=False)
    progress_pct = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
