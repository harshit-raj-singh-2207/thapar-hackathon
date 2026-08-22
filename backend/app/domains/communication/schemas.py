from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# ---------------- AAC Categories ----------------
class AACCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: str = "⭐"
    color: str = "#2563EB"
    order: int = 0
    is_system: bool = True

class AACCategoryCreate(AACCategoryBase):
    pass

class AACCategoryResponse(AACCategoryBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- Picture Communication Cards ----------------
class AACCardBase(BaseModel):
    category_id: Optional[str] = None
    label: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = None
    spoken_text: Optional[str] = None
    keyword: Optional[str] = None
    icon: str = "💬"
    image_url: Optional[str] = None
    part_of_speech: str = "noun"
    bg_color: str = "#FFFFFF"
    text_color: str = "#0F172A"
    is_quick_need: bool = False
    is_active: bool = True
    display_order: int = 0
    child_id: Optional[str] = None

class AACCardCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = None
    category_id: Optional[str] = None
    category: Optional[str] = None  # category name or ID alias
    spoken_text: Optional[str] = None
    keyword: Optional[str] = None
    icon: str = "💬"
    image_url: Optional[str] = None
    part_of_speech: str = "noun"
    bg_color: str = "#FFFFFF"
    text_color: str = "#0F172A"
    is_quick_need: bool = False
    is_active: bool = True
    display_order: int = 0
    child_id: Optional[str] = None

class AACCardUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = None
    category_id: Optional[str] = None
    category: Optional[str] = None
    spoken_text: Optional[str] = None
    keyword: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    part_of_speech: Optional[str] = None
    bg_color: Optional[str] = None
    text_color: Optional[str] = None
    is_quick_need: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    child_id: Optional[str] = None

class AACCardResponse(AACCardBase):
    id: str
    category_name: Optional[str] = None
    usage_count: int = 0
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- NLP & Speech Generation ----------------
class AACSentenceBuildRequest(BaseModel):
    child_id: Optional[str] = None
    card_ids: Optional[List[str]] = None
    token_ids: Optional[List[str]] = None
    tokens: Optional[List[str]] = None
    emotion: Optional[str] = None
    style: Optional[str] = "natural"
    context: Optional[dict] = None
    save_log: bool = True

class AACSentenceBuildResponse(BaseModel):
    tokens: List[str]
    labels: List[str]
    card_ids: List[str] = []
    constructed_sentence: str
    sentence: str
    generated_sentence: str
    simplified_sentence: Optional[str] = None
    suggested_alternatives: List[str] = []
    audio_hint: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SentenceBuildRequest(BaseModel):
    child_id: Optional[str] = None
    tokens: Optional[List[str]] = Field(default=None, description="List of AAC card labels or word tokens")
    sentence: Optional[str] = Field(default=None, description="Raw sentence string to expand or structure")
    emotion: Optional[str] = None
    context: Optional[str] = None
    style: Optional[str] = "natural"  # natural, simple, polite, urgent

class SentenceBuildResponse(BaseModel):
    raw_tokens: List[str] = []
    generated_sentence: str
    simplified_sentence: Optional[str] = None
    suggestions: List[str] = []
    suggested_alternatives: List[str] = []
    is_fallback: bool = False
    audio_hint: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Aliases for explicit naming
SentenceGenerationRequest = SentenceBuildRequest
SentenceGenerationResponse = SentenceBuildResponse


class SimplifyTextRequest(BaseModel):
    child_id: Optional[str] = None
    text: Optional[str] = Field(default=None, description="Complex text to simplify")
    sentence: Optional[str] = Field(default=None, description="Sentence to simplify")
    target_level: Optional[str] = "easy"  # easy, pictorial, short
    context: Optional[str] = None

class SimplifyTextResponse(BaseModel):
    original_text: str
    simplified_text: str
    simplified_sentence: Optional[str] = None
    key_points: List[str] = []
    matching_aac_tokens: List[str] = []
    suggestions: List[str] = []
    is_fallback: bool = False

    model_config = ConfigDict(from_attributes=True)

# Aliases for explicit naming
SentenceSimplificationRequest = SimplifyTextRequest
SentenceSimplificationResponse = SimplifyTextResponse


class TextToSpeechRequest(BaseModel):
    child_id: Optional[str] = None
    text: Optional[str] = Field(default=None, description="Text to convert to speech")
    voice: Optional[str] = "friendly_child"   # friendly_child, calm_female, clear_male, gentle_neutral
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech pitch multiplier")
    language: Optional[str] = "en-US"
    emotion: Optional[str] = None

class AACSpeechRequest(BaseModel):
    child_id: Optional[str] = None
    tokens: List[str] = Field(..., description="List of AAC card tokens/labels to convert to speech")
    voice: Optional[str] = "friendly_child"
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech pitch multiplier")
    language: Optional[str] = "en-US"
    emotion: Optional[str] = None

class AISentenceSpeechRequest(BaseModel):
    child_id: Optional[str] = None
    sentence: str = Field(..., description="AI generated sentence to convert to speech")
    emotion: Optional[str] = None
    voice: Optional[str] = "friendly_child"
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech pitch multiplier")
    language: Optional[str] = "en-US"

class TextToSpeechResponse(BaseModel):
    text: str
    audio_url: Optional[str] = None
    phonetic_guide: Optional[str] = None
    ssml_hint: Optional[str] = None
    web_speech_config: Optional[dict] = None
    duration_estimate_sec: float = 1.5
    voice_used: str = "friendly_child"
    is_fallback: bool = False
    provider: str = "web_speech_api"

    model_config = ConfigDict(from_attributes=True)




# ---------------- Emotion Check-in ----------------
class EmotionCheckinRequest(BaseModel):
    emotion: str = Field(..., min_length=1, max_length=50)
    intensity: int = Field(5, ge=1, le=10, description="Intensity level from 1 to 10")
    child_id: Optional[str] = None
    note: Optional[str] = None

class EmotionCheckinResponse(BaseModel):
    id: str
    child_id: Optional[str] = None
    user_id: Optional[str] = None
    emotion: str
    intensity: int
    note: Optional[str] = None
    icon: Optional[str] = "❤️"
    calming_strategies: List[str] = []
    sensory_tip: Optional[str] = None
    recommended_phrases: List[str] = []
    communication_suggestions: List[str] = []
    created_at: Optional[datetime] = None
    timestamp: Optional[datetime] = None
    is_fallback: bool = False

    model_config = ConfigDict(from_attributes=True)

class EmotionSuggestionsResponse(BaseModel):
    emotion: str
    intensity: int = 5
    icon: str = "❤️"
    calming_strategies: List[str] = []
    sensory_tip: str
    recommended_phrases: List[str] = []
    communication_suggestions: List[str] = []
    is_fallback: bool = False

    model_config = ConfigDict(from_attributes=True)



# ---------------- Quick & Saved Favorite Phrases ----------------
class SavedPhraseCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    child_id: Optional[str] = None
    tokens: List[str] = []
    category: str = "Quick Communication"
    icon: str = "⭐"
    is_favorite: bool = True

class SavedPhraseResponse(BaseModel):
    id: str
    child_id: Optional[str] = None
    user_id: Optional[str] = None
    text: str
    tokens: List[str] = []
    category: str
    icon: str
    is_favorite: bool = True
    usage_count: int = 0
    use_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PhraseUsageRequest(BaseModel):
    phrase_id: Optional[str] = None
    text: Optional[str] = None
    child_id: Optional[str] = None
    emotion: Optional[str] = None

class PhraseUsageResponse(BaseModel):
    phrase_id: Optional[str] = None
    text: str
    usage_count: int
    spoken_sentence: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    log_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)




# ---------------- Communication Logs (History) ----------------
class CommunicationLogCreate(BaseModel):
    sentence: str = Field(..., min_length=1, max_length=500)
    child_id: Optional[str] = None
    tokens: List[str] = []
    source: str = "aac"  # aac, quick_need, ai_sentence, emotion, speech
    category: Optional[str] = None
    emotion: Optional[str] = None
    audio_played: bool = True
    is_favorite: bool = False

class CommunicationLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    child_id: Optional[str] = None
    sentence: str
    tokens: List[str] = []
    source: str
    category: Optional[str] = None
    emotion: Optional[str] = None
    audio_played: bool
    is_favorite: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CommunicationHistoryFilter(BaseModel):
    """Filter parameters for history search."""
    child_id: Optional[str] = None
    source: Optional[str] = None          # aac, quick_need, ai_sentence, emotion, speech
    category: Optional[str] = None
    emotion: Optional[str] = None
    favorites_only: Optional[bool] = None
    search: Optional[str] = None          # full-text search in sentence
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class CommunicationHistoryPage(BaseModel):
    """Paginated communication history response."""
    items: List[CommunicationLogResponse]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool

    model_config = ConfigDict(from_attributes=True)
