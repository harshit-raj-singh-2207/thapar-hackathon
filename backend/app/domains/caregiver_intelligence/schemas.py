from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class BasicCaregiverInsight(BaseModel):
    current_status: str
    latest_emotion: Optional[dict[str, Any]] = None
    safety_state: str
    active_sos: bool = False
    routine_progress: Optional[float] = Field(default=None, ge=0, le=100)
    important_alerts: list[dict[str, Any]] = Field(default_factory=list)


class AnalyticsPeriod(BaseModel):
    period_days: int
    emotion_trends: dict[str, int] = Field(default_factory=dict)
    sensory_trigger_patterns: dict[str, int] = Field(default_factory=dict)
    communication_usage_trends: dict[str, int] = Field(default_factory=dict)
    routine_completion: Optional[float] = Field(default=None, ge=0, le=100)
    safety_events: dict[str, int] = Field(default_factory=dict)
    learning_progress: dict[str, Any] = Field(default_factory=dict)
    game_progress: dict[str, Any] = Field(default_factory=dict)


class PremiumCaregiverAnalytics(BaseModel):
    weekly: AnalyticsPeriod
    monthly: AnalyticsPeriod
    calm_strategy_effectiveness: dict[str, Any]
    progress_insights: list[str] = Field(default_factory=list)
    downloadable_reports_available: bool = True
    multi_week_comparisons_available: bool = True


class CaregiverInsightsResponse(BaseModel):
    user_id: str
    plan: str
    basic: BasicCaregiverInsight
    premium_analytics_available: bool
    premium: Optional[PremiumCaregiverAnalytics] = None
    generated_at: datetime
    disclaimer: str = "This is an observed activity summary and not a medical diagnosis."
