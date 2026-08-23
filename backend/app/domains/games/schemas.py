from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# ---------------- Game Catalog Schemas ----------------
class GameTaskOption(BaseModel):
    id: str
    label: str
    icon: Optional[str] = None
    is_correct: bool = False

    model_config = ConfigDict(from_attributes=True)


class GameTaskItem(BaseModel):
    id: str
    prompt: str
    instruction: Optional[str] = None
    task_type: str = "matching"  # matching, multiple_choice, sequence, emotion_select, visual_find
    aac_token: Optional[str] = None
    emotion_target: Optional[str] = None
    options: List[GameTaskOption] = []
    points: int = 1

    model_config = ConfigDict(from_attributes=True)


class GameBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    category: str = Field(..., description="Communication, Emotion, Memory, Matching, Focus, Learning, Social Skills, Daily Life Skills")
    description: Optional[str] = None
    icon: str = "🎮"
    color: str = "#3B82F6"
    difficulty: str = "easy"
    min_age: int = 4
    max_age: int = 14
    is_emergency_recommended: bool = True
    skill_tags: List[str] = []
    instructions: Optional[str] = None
    tasks_data: List[Dict[str, Any]] = []


class GameCreate(GameBase):
    pass


class GameResponse(GameBase):
    id: str
    tasks_count: int = 0
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- Game Session Schemas ----------------
class GameSessionStartRequest(BaseModel):
    game_id: str
    child_id: Optional[str] = None


class GameSessionStartResponse(BaseModel):
    session_id: str
    game_id: str
    game_title: str
    category: str
    child_id: Optional[str] = None
    status: str = "in_progress"
    tasks: List[Dict[str, Any]] = []
    total_tasks: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class GameSessionAnswerRequest(BaseModel):
    task_index: int
    selected_option_id: str
    time_spent_sec: Optional[int] = 0


class GameSessionAnswerResponse(BaseModel):
    session_id: str
    task_index: int
    is_correct: bool
    current_score: int
    encouraging_message: str
    reinforcement_cue: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GameSessionCompleteRequest(BaseModel):
    duration_sec: Optional[int] = 60
    notes: Optional[str] = None


class GameAchievementResponse(BaseModel):
    id: str
    child_id: str
    badge_key: str
    title: str
    description: Optional[str] = None
    icon: str = "🏆"
    category: str = "General"
    unlocked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GameSessionCompleteResponse(BaseModel):
    session_id: str
    game_id: str
    game_title: str
    category: str
    child_id: Optional[str] = None
    score: int
    max_score: int
    accuracy_pct: float
    stars: int  # 0 to 3
    duration_sec: int
    status: str = "completed"
    feedback: str
    learning_progress_updated: bool = False
    learning_topic_connected: Optional[str] = None
    communication_reinforced: Optional[str] = None
    new_achievements: List[GameAchievementResponse] = []
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class GameSessionResponse(BaseModel):
    id: str
    game_id: str
    child_id: Optional[str] = None
    user_id: Optional[str] = None
    status: str
    score: int
    max_score: int
    stars: int
    duration_sec: int
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- Progress & Category Schemas ----------------
class GameProgressResponse(BaseModel):
    id: str
    child_id: str
    game_id: str
    skill_category: str
    total_plays: int
    highest_score: int
    total_stars: int
    mastery_level: str
    last_played_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GameCategorySummary(BaseModel):
    category: str
    display_name: str
    icon: str
    color: str
    description: str
    games_count: int
    mastery_level: str = "beginner"


# ---------------- Recommendations & Emergency Dashboards ----------------
class GameRecommendationItem(BaseModel):
    game_id: str
    title: str
    category: str
    icon: str
    color: str
    reason: str
    recommended_focus: str
    benefit: str

    model_config = ConfigDict(from_attributes=True)


class GameRecommendationsResponse(BaseModel):
    child_id: Optional[str] = None
    recommendations: List[GameRecommendationItem] = []
    is_emergency_mode: bool = False
    summary: str
    is_fallback: bool = False

    model_config = ConfigDict(from_attributes=True)


class EmergencyGamesHomeResponse(BaseModel):
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    is_emergency_mode: bool = False
    emergency_status: str = "inactive"
    games_enabled: bool = True
    categories: List[GameCategorySummary] = []
    featured_games: List[GameResponse] = []
    emergency_recommended_games: List[GameResponse] = []
    recent_sessions: List[GameSessionResponse] = []
    recent_achievements: List[GameAchievementResponse] = []
    personalized_recommendations: List[GameRecommendationItem] = []
    stats: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class CaregiverGamesReviewResponse(BaseModel):
    child_id: str
    child_name: str
    caregiver_id: str
    is_emergency_mode: bool = False
    emergency_status: str = "inactive"
    total_games_played: int = 0
    total_stars_earned: int = 0
    total_achievements_unlocked: int = 0
    skill_mastery_breakdown: Dict[str, Any] = {}
    recent_sessions: List[GameSessionResponse] = []
    achievements: List[GameAchievementResponse] = []
    recommended_activities: List[GameRecommendationItem] = []
    summary_stats: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
