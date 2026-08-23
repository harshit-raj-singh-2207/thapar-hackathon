from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class RoutineStepBase(BaseModel):
    step_number: int = 1
    title: str
    instruction: Optional[str] = None
    icon: str = "✓"
    duration_sec: int = 60
    is_completed: bool = False

class RoutineStepCreate(RoutineStepBase):
    pass

class RoutineStepResponse(RoutineStepBase):
    id: str
    routine_id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class RoutineBase(BaseModel):
    title: str
    time_of_day: str = "morning"
    icon: str = "🌅"
    color: str = "#3B82F6"
    is_active: bool = True

class RoutineCreate(RoutineBase):
    steps: List[RoutineStepCreate] = []

class RoutineResponse(RoutineBase):
    id: str
    streak_days: int = 0
    steps: List[RoutineStepResponse] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AdaptiveRoutineRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=300)
    days: int = Field(default=1, ge=1, le=14)
    routine_id: Optional[str] = None
    change_reason: Optional[str] = Field(default=None, max_length=500)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class AdaptiveRoutineResponse(BaseModel):
    recommendation: str
    suggested_steps: List[str]
    days: int
    source: str
    budget_status: str
    fallback_reason: Optional[str] = None


class RoutineShareCreate(BaseModel):
    caregiver_user_id: str = Field(min_length=1, max_length=64)
    can_edit: bool = True


class RoutineShareResponse(BaseModel):
    id: str
    routine_id: str
    caregiver_user_id: str
    can_edit: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TaskBreakdownRequest(BaseModel):
    task_title: str
    custom_context: Optional[str] = None

class TaskBreakdownResponse(BaseModel):
    task_title: str
    steps: List[Dict[str, Any]]
    total_estimated_duration_sec: int
    encouragement: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "Daily Living"
    icon: str = "📋"
    steps_data: List[Dict[str, Any]] = []

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    icon: str
    is_completed: bool
    steps_data: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReminderCreate(BaseModel):
    title: str
    time_str: str
    frequency: str = "Daily"
    category: str = "Hydration"
    icon: str = "⏰"
    is_active: bool = True

class ReminderResponse(BaseModel):
    id: str
    title: str
    time_str: str
    frequency: str
    category: str
    icon: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TutorAskRequest(BaseModel):
    question: str
    topic: Optional[str] = "General"
    session_id: Optional[str] = None

class TutorAskResponse(BaseModel):
    session_id: str
    question: str
    reply: str
    simple_analogy: Optional[str] = None
    follow_up_questions: List[str] = []
    icon: str = "💡"
    recommended_activity: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class LearningTopicResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str] = None
    icon: str
    color: str
    modules: List[Dict[str, Any]] = []
    is_completed: bool
    progress_pct: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EmergencyLearningPlanResponse(BaseModel):
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    is_emergency_mode: bool = False
    emergency_status: str = "inactive"  # active, scheduled, expired, inactive
    learning_enabled: bool = True
    daily_routines: List[RoutineResponse] = []
    daily_tasks: List[TaskResponse] = []
    reminders: List[ReminderResponse] = []
    learning_topics: List[LearningTopicResponse] = []
    recommended_activities: List[Dict[str, Any]] = []
    ai_tutor_hint: Optional[str] = None
    summary_stats: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class CaregiverLearningReviewResponse(BaseModel):
    child_id: str
    child_name: str
    caregiver_id: str
    is_emergency_mode: bool = False
    emergency_status: str = "inactive"
    completed_tasks: List[TaskResponse] = []
    in_progress_tasks: List[TaskResponse] = []
    routines: List[RoutineResponse] = []
    active_reminders: List[ReminderResponse] = []
    learning_topics: List[LearningTopicResponse] = []
    recommended_activities: List[Dict[str, Any]] = []
    overall_completion_rate: float = 0.0
    summary_stats: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


