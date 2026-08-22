from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True

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

    class Config:
        orm_mode = True
