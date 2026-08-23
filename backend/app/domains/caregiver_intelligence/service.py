from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.communication.models import CommunicationLog, EmotionRecord
from app.domains.entitlements.service import EntitlementService, Feature
from app.domains.learning.models import Routine, Task
from app.domains.sensory.models import SensoryStateRecord
from app.models.child import Child
from app.models.emergency import EmergencyAlert
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.domains.caregiver_intelligence.schemas import (
    AnalyticsPeriod,
    BasicCaregiverInsight,
    CaregiverInsightsResponse,
    PremiumCaregiverAnalytics,
)


class CaregiverIntelligenceService:
    """Read-only deterministic insights over existing NIVARA domain records."""

    def __init__(self, db: Session):
        self.db = db

    def _linked_child(self, user_id: str, caregiver: User) -> Child:
        if str(getattr(caregiver, "role", "")).lower() not in {"caregiver", "admin"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Caregiver access is required.",
            )
        child = self.db.query(Child).filter(Child.id == user_id).first()
        if child is None:
            raise HTTPException(status_code=404, detail="Linked user not found.")
        if child.caregiver_id != caregiver.id and getattr(caregiver, "role", None) != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view insights for this user.",
            )
        return child

    @staticmethod
    def _counts(rows, attribute: str) -> dict[str, int]:
        return dict(Counter(str(getattr(row, attribute) or "unknown") for row in rows))

    def _period(self, child: Child, caregiver_id: str, days: int) -> AnalyticsPeriod:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        emotions = self.db.query(EmotionRecord).filter(
            EmotionRecord.child_id == child.id, EmotionRecord.created_at >= since
        ).all()
        sensory = self.db.query(SensoryStateRecord).filter(
            SensoryStateRecord.user_id == caregiver_id,
            SensoryStateRecord.created_at >= since,
        ).all()
        communications = self.db.query(CommunicationLog).filter(
            CommunicationLog.child_id == child.id,
            CommunicationLog.is_deleted.is_(False),
            CommunicationLog.created_at >= since,
        ).all()
        events = self.db.query(SafetyEvent).filter(
            SafetyEvent.child_id == child.id, SafetyEvent.created_at >= since
        ).all()
        routines = self.db.query(Routine).filter(Routine.user_id == caregiver_id).all()
        steps = [step for routine in routines for step in routine.steps]
        completion = round(100 * sum(bool(step.is_completed) for step in steps) / len(steps), 2) if steps else None
        tasks = self.db.query(Task).filter(
            Task.user_id == caregiver_id, Task.created_at >= since
        ).all()
        return AnalyticsPeriod(
            period_days=days,
            emotion_trends=self._counts(emotions, "emotion"),
            sensory_trigger_patterns=self._counts(sensory, "sensory_state"),
            communication_usage_trends=self._counts(communications, "source"),
            routine_completion=completion,
            safety_events=self._counts(events, "event_type"),
            learning_progress={
                "status": "available" if tasks else "unavailable",
                "tasks_total": len(tasks),
                "tasks_completed": sum(bool(task.is_completed) for task in tasks),
            },
            game_progress={"status": "unavailable", "reason": "No user-scoped game history is stored."},
        )

    def get_insights(self, user_id: str, caregiver: User) -> CaregiverInsightsResponse:
        child = self._linked_child(user_id, caregiver)
        latest_emotion = self.db.query(EmotionRecord).filter(
            EmotionRecord.child_id == child.id
        ).order_by(EmotionRecord.created_at.desc()).first()
        active_sos = self.db.query(EmergencyAlert).filter(
            EmergencyAlert.child_id == child.id, EmergencyAlert.status == "active"
        ).first() is not None
        alerts = self.db.query(SafetyEvent).filter(
            SafetyEvent.child_id == child.id,
            SafetyEvent.severity.in_(("warning", "critical")),
        ).order_by(SafetyEvent.created_at.desc()).limit(5).all()
        routine = self.db.query(Routine).filter(
            Routine.user_id == caregiver.id, Routine.is_active.is_(True)
        ).order_by(Routine.created_at.desc()).first()
        steps = list(routine.steps) if routine else []
        routine_progress = round(100 * sum(bool(step.is_completed) for step in steps) / len(steps), 2) if steps else None
        safety_state = "EMERGENCY" if active_sos else str(child.current_status or "unknown").upper()
        basic = BasicCaregiverInsight(
            current_status=child.current_status or "unknown",
            latest_emotion=(
                {"emotion": latest_emotion.emotion, "intensity": latest_emotion.intensity,
                 "updated_at": latest_emotion.created_at}
                if latest_emotion else None
            ),
            safety_state=safety_state,
            active_sos=active_sos,
            routine_progress=routine_progress,
            important_alerts=[
                {"type": row.event_type, "severity": row.severity, "title": row.title,
                 "created_at": row.created_at} for row in alerts
            ],
        )
        entitlements = EntitlementService(self.db)
        premium_allowed = entitlements.has_feature_access(
            caregiver.id, Feature.CAREGIVER_INTELLIGENCE.value
        )
        premium = None
        if premium_allowed:
            weekly = self._period(child, caregiver.id, 7)
            monthly = self._period(child, caregiver.id, 30)
            insights = [
                f"Observed activity pattern: {sum(weekly.communication_usage_trends.values())} communication uses in the last 7 days.",
                f"Progress summary: routine completion is {weekly.routine_completion}% for currently stored routine steps."
                if weekly.routine_completion is not None else
                "Progress summary: there is not enough routine history yet.",
            ]
            premium = PremiumCaregiverAnalytics(
                weekly=weekly,
                monthly=monthly,
                calm_strategy_effectiveness={
                    "status": "insufficient_data",
                    "reason": "Calm-strategy outcomes are not currently recorded.",
                },
                progress_insights=insights,
                downloadable_reports_available=entitlements.has_feature_access(
                    caregiver.id, Feature.CAREGIVER_REPORTS.value
                ),
                multi_week_comparisons_available=entitlements.has_feature_access(
                    caregiver.id, Feature.CAREGIVER_MULTI_WEEK.value
                ),
            )
        return CaregiverInsightsResponse(
            user_id=user_id,
            plan=entitlements.get_plan(caregiver.id).value,
            basic=basic,
            premium_analytics_available=premium_allowed,
            premium=premium,
            generated_at=datetime.now(timezone.utc),
        )
