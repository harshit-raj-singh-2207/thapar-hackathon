import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Game(Base):
    __tablename__ = "games"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # Communication, Emotion, Memory, Matching, Focus, Learning, Social Skills, Daily Life Skills
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="🎮")
    color = Column(String(50), default="#3B82F6")
    difficulty = Column(String(50), default="easy")  # easy, medium, adaptive
    min_age = Column(Integer, default=4)
    max_age = Column(Integer, default=14)
    is_emergency_recommended = Column(Boolean, default=True, index=True)
    skill_tags = Column(JSON, default=list)
    instructions = Column(Text, nullable=True)
    tasks_data = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("GameSession", back_populates="game_rel", cascade="all, delete-orphan")


class GameSession(Base):
    __tablename__ = "game_sessions"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(64), ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    child_id = Column(String(64), ForeignKey("children.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), default="in_progress", index=True)  # in_progress, completed, abandoned
    score = Column(Integer, default=0)
    max_score = Column(Integer, default=10)
    stars = Column(Integer, default=0)  # 0 to 3
    duration_sec = Column(Integer, default=0)
    answers_data = Column(JSON, default=list)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    game_rel = relationship("Game", back_populates="sessions")


class GameProgress(Base):
    __tablename__ = "game_progress"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(64), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    game_id = Column(String(64), ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_category = Column(String(50), nullable=False, index=True)
    total_plays = Column(Integer, default=0)
    highest_score = Column(Integer, default=0)
    total_stars = Column(Integer, default=0)
    mastery_level = Column(String(50), default="beginner")  # beginner, practicing, mastered
    last_played_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GameAchievement(Base):
    __tablename__ = "game_achievements"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(64), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_key = Column(String(100), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="🏆")
    category = Column(String(50), default="General")
    unlocked_at = Column(DateTime, default=datetime.utcnow, index=True)
