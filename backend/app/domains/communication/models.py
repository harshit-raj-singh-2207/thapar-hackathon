import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AACCategory(Base):
    __tablename__ = "aac_categories"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, index=True)
    icon = Column(String(50), nullable=False, default="⭐")
    color = Column(String(50), nullable=False, default="#2563EB")
    order = Column(Integer, default=0)
    is_system = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cards = relationship("AACCard", back_populates="category_rel", cascade="all, delete-orphan")


class AACCard(Base):
    __tablename__ = "aac_cards"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(64), ForeignKey("aac_categories.id"), nullable=True, index=True)
    label = Column(String(100), nullable=False)
    spoken_text = Column(String(200), nullable=True)
    keyword = Column(String(100), nullable=True, index=True)
    icon = Column(String(50), nullable=False, default="💬")
    image_url = Column(String(500), nullable=True)
    part_of_speech = Column(String(50), default="noun")  # noun, verb, pronoun, adjective, preposition
    bg_color = Column(String(50), default="#FFFFFF")
    text_color = Column(String(50), default="#0F172A")
    usage_count = Column(Integer, default=0)
    is_quick_need = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)
    child_id = Column(String(64), ForeignKey("children.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category_rel = relationship("AACCategory", back_populates="cards")


class SavedPhrase(Base):
    __tablename__ = "saved_phrases"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(64), ForeignKey("children.id"), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    text = Column(String(500), nullable=False)
    tokens = Column(JSON, default=list)  # list of token labels / card ids
    category = Column(String(100), default="Quick Communication")
    icon = Column(String(50), default="⭐")
    is_favorite = Column(Boolean, default=True, index=True)
    usage_count = Column(Integer, default=0)
    use_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class EmotionRecord(Base):
    __tablename__ = "emotion_records"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String(64), ForeignKey("children.id"), nullable=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=True, index=True)
    emotion = Column(String(50), nullable=False)  # happy, calm, anxious, sad, angry, overwhelmed, tired, excited, scared, frustrated
    intensity = Column(Integer, default=5)  # 1-10
    note = Column(Text, nullable=True)
    icon = Column(String(50), default="❤️")
    calming_strategies = Column(JSON, default=list)
    sensory_tip = Column(String(500), nullable=True)
    recommended_phrases = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)



class CommunicationLog(Base):
    __tablename__ = "communication_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    child_id = Column(String(64), ForeignKey("children.id", ondelete="SET NULL"), nullable=True, index=True)
    sentence = Column(String(500), nullable=False, index=True)
    tokens = Column(JSON, default=list)           # list of token labels used
    source = Column(String(50), default="aac", index=True)   # aac, quick_need, ai_sentence, emotion, speech
    category = Column(String(100), nullable=True, index=True)
    emotion = Column(String(50), nullable=True, index=True)
    audio_played = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False, index=True)
    is_deleted = Column(Boolean, default=False, index=True)  # soft delete
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
