from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.domains.learning.repository import LearningRepository
from app.domains.learning.models import Routine, Task, Reminder, LearningTopic
from app.domains.learning.schemas import (
    RoutineCreate,
    RoutineResponse,
    TaskBreakdownRequest,
    TaskBreakdownResponse,
    TaskCreate,
    TaskResponse,
    ReminderCreate,
    ReminderResponse,
    TutorAskRequest,
    TutorAskResponse,
    LearningTopicResponse,
    EmergencyLearningPlanResponse,
    CaregiverLearningReviewResponse,
)
from app.domains.learning.routine_service import RoutineService
from app.domains.learning.task_service import TaskService
from app.domains.learning.tutor_service import TutorService
from app.models.child import Child
from app.models.user import User
from app.models.emergency_mode import EmergencyMode

class LearningService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LearningRepository(db)
        self.routine_service = RoutineService(db)
        self.task_service = TaskService(db)
        self.tutor_service = TutorService(db)

    def _verify_child_access(self, child_id: str, current_user: Optional[User] = None) -> Child:
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        if current_user and current_user.role == "caregiver":
            if child.caregiver_id != current_user.id:
                raise HTTPException(status_code=403, detail="Unauthorized caregiver for this child")
        return child

    # Routines
    def get_routines(self, user_id: Optional[str] = None) -> List[Routine]:
        return self.routine_service.get_all_routines(user_id=user_id)

    def get_routine_by_id(self, routine_id: str) -> Optional[Routine]:
        return self.routine_service.get_routine_by_id(routine_id)

    def create_routine(self, req: RoutineCreate, user_id: Optional[str] = None) -> Routine:
        return self.routine_service.create_routine(req, user_id=user_id)

    def toggle_routine_step(self, step_id: str, user_id: Optional[str] = None):
        return self.routine_service.toggle_step(step_id, user_id=user_id)

    def reset_routine(self, routine_id: str, user_id: Optional[str] = None):
        return self.routine_service.reset_routine(routine_id, user_id=user_id)

    def share_routine(self, routine_id: str, owner_user_id: str, caregiver_user_id: str, can_edit: bool):
        return self.routine_service.share_routine(
            routine_id, owner_user_id, caregiver_user_id, can_edit
        )

    # Tasks
    def breakdown_task_ai(self, req: TaskBreakdownRequest) -> TaskBreakdownResponse:
        return self.task_service.breakdown_task_ai(req)

    def get_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        return self.task_service.get_all_tasks(user_id=user_id)

    def create_task(self, req: TaskCreate, user_id: Optional[str] = None) -> Task:
        return self.task_service.create_task(req, user_id=user_id)

    def update_task_step_progress(self, task_id: str, step_index: int, is_completed: bool, user_id: Optional[str] = None) -> Optional[Task]:
        return self.task_service.update_task_progress(
            task_id, step_index, is_completed, user_id=user_id
        )

    # Reminders
    def get_reminders(self, user_id: Optional[str] = None) -> List[Reminder]:
        return self.repo.get_reminders(user_id=user_id)

    def create_reminder(self, req: ReminderCreate, user_id: Optional[str] = None) -> Reminder:
        rem = Reminder(
            user_id=user_id,
            title=req.title,
            time_str=req.time_str,
            frequency=req.frequency,
            category=req.category,
            icon=req.icon,
            is_active=req.is_active,
        )
        return self.repo.create_reminder(rem)

    def toggle_reminder(self, reminder_id: str) -> Optional[Reminder]:
        return self.repo.toggle_reminder(reminder_id)

    # Tutor
    def ask_tutor(self, req: TutorAskRequest, user_id: Optional[str] = None) -> TutorAskResponse:
        return self.tutor_service.ask_tutor(req, user_id=user_id)

    # Topics
    def get_topics(self) -> List[LearningTopic]:
        return self.repo.get_topics()

    def update_topic_progress(self, topic_id: str, progress_pct: int, is_completed: bool) -> Optional[LearningTopic]:
        return self.repo.update_topic_progress(topic_id, progress_pct, is_completed)

    # Emergency Learning Plan & Caregiver Review
    def get_emergency_learning_plan(
        self,
        child_id: Optional[str] = None,
        current_user: Optional[User] = None
    ) -> EmergencyLearningPlanResponse:
        """
        Retrieves unified home-based emergency learning plan for remote isolation.
        Connects routines, visual task breakdowns, reminders, learning topics, and AI tutor suggestions.
        """
        child_name = None
        if child_id:
            child = self._verify_child_access(child_id, current_user)
            child_name = getattr(child, "name", None) or getattr(child, "full_name", None)
        elif current_user:
            if getattr(current_user, "children", None) and len(current_user.children) > 0:
                c = current_user.children[0]
                child_id = c.id
                child_name = getattr(c, "name", None) or getattr(c, "full_name", None)

        # Check Emergency Mode
        emg = None
        if child_id:
            emg = self.db.query(EmergencyMode).filter(EmergencyMode.child_id == child_id).first()

        is_emg_active = False
        emg_status = "inactive"
        learning_enabled = True

        if emg:
            eff = emg.effective_status
            if eff == "expired" and emg.status != "expired":
                emg.status = "expired"
                emg.is_active = False
                self.db.commit()
            emg_status = emg.status
            is_emg_active = (emg.status == "active" and emg.is_active)
            if emg.preferences:
                learning_enabled = getattr(emg.preferences, "learning_enabled", True)

        routines = self.get_routines(user_id=child_id)
        tasks = self.get_tasks(user_id=child_id)
        reminders = self.get_reminders(user_id=child_id)
        topics = self.get_topics()

        # Compute summary stats
        total_routines = len(routines)
        completed_steps = sum(1 for r in routines for s in (r.steps or []) if s.is_completed)
        total_steps = sum(len(r.steps or []) for r in routines)
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.is_completed)
        streak_days = max((r.streak_days or 0 for r in routines), default=0)

        summary_stats = {
            "total_routines": total_routines,
            "completed_routine_steps": completed_steps,
            "total_routine_steps": total_steps,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "active_reminders_count": len([r for r in reminders if r.is_active]),
            "topics_count": len(topics),
            "streak_days": streak_days,
        }

        if is_emg_active and learning_enabled:
            recommended_activities = [
                {
                    "id": "rec-morning-routine",
                    "title": "Morning Sunshine Routine",
                    "type": "routine",
                    "icon": "🌅",
                    "reason": "Structured daily start for emotional stability and focus at home.",
                    "duration_min": 15,
                },
                {
                    "id": "rec-wash-hands",
                    "title": "Wash Hands Step-by-Step",
                    "type": "task",
                    "icon": "🧼",
                    "reason": "Essential home hygiene practice with visual micro-steps.",
                    "duration_min": 2,
                },
                {
                    "id": "rec-hydration-break",
                    "title": "Hydration & Sensory Pause",
                    "type": "break",
                    "icon": "💧",
                    "reason": "Regular sensory regulation breaks prevent sensory overload during home study.",
                    "duration_min": 5,
                },
                {
                    "id": "rec-social-story",
                    "title": "When Noises Get Too Loud",
                    "type": "topic",
                    "icon": "🎧",
                    "reason": "Social-emotional regulation story for home quiet corners.",
                    "duration_min": 10,
                },
                {
                    "id": "rec-bedtime-winddown",
                    "title": "Calm Bedtime Wind-Down",
                    "type": "routine",
                    "icon": "🌙",
                    "reason": "Predictable evening routine promoting restful sleep during isolation.",
                    "duration_min": 15,
                },
            ]
            ai_tutor_hint = "🌟 Hi! Nivi is here with you! During our home-learning period, taking small steps and drinking water makes learning super fun!"

            return EmergencyLearningPlanResponse(
                child_id=child_id,
                child_name=child_name,
                is_emergency_mode=True,
                emergency_status=emg_status,
                learning_enabled=learning_enabled,
                daily_routines=[RoutineResponse.model_validate(r) for r in routines],
                daily_tasks=[TaskResponse.model_validate(t) for t in tasks],
                reminders=[ReminderResponse.model_validate(rem) for rem in reminders],
                learning_topics=[LearningTopicResponse.model_validate(top) for top in topics],
                recommended_activities=recommended_activities,
                ai_tutor_hint=ai_tutor_hint,
                summary_stats=summary_stats,
            )
        else:
            return EmergencyLearningPlanResponse(
                child_id=child_id,
                child_name=child_name,
                is_emergency_mode=False,
                emergency_status=emg_status,
                learning_enabled=learning_enabled,
                daily_routines=[RoutineResponse.model_validate(r) for r in routines],
                daily_tasks=[TaskResponse.model_validate(t) for t in tasks],
                reminders=[ReminderResponse.model_validate(rem) for rem in reminders],
                learning_topics=[LearningTopicResponse.model_validate(top) for top in topics],
                recommended_activities=[],
                ai_tutor_hint=None,
                summary_stats=summary_stats,
            )

    def get_caregiver_learning_review(
        self,
        child_id: str,
        current_user: User
    ) -> CaregiverLearningReviewResponse:
        """
        Caregiver remote supervision dashboard view for reviewing child's learning,
        routine progress, micro-tasks, and AI recommendations during 90-day isolation.
        """
        child = self._verify_child_access(child_id, current_user)
        child_name = getattr(child, "name", None) or getattr(child, "full_name", None) or "Child"

        emg = self.db.query(EmergencyMode).filter(EmergencyMode.child_id == child_id).first()
        is_emg_active = bool(emg and emg.status == "active" and emg.is_active and emg.effective_status == "active")
        emg_status = emg.status if emg else "inactive"

        routines = self.get_routines(user_id=child_id)
        tasks = self.get_tasks(user_id=child_id)
        reminders = self.get_reminders(user_id=child_id)
        topics = self.get_topics()

        completed_tasks = [t for t in tasks if t.is_completed]
        in_progress_tasks = [t for t in tasks if not t.is_completed]
        active_reminders = [r for r in reminders if r.is_active]

        # Calculate overall completion rate
        total_routine_steps = sum(len(r.steps or []) for r in routines)
        completed_routine_steps = sum(1 for r in routines for s in (r.steps or []) if s.is_completed)
        total_tasks_count = len(tasks)
        completed_tasks_count = len(completed_tasks)
        total_topics_count = len(topics)
        completed_topics_count = sum(1 for top in topics if top.is_completed or (top.progress_pct or 0) >= 100)

        total_items = total_routine_steps + total_tasks_count + total_topics_count
        completed_items = completed_routine_steps + completed_tasks_count + completed_topics_count
        overall_rate = round((completed_items / total_items) * 100, 1) if total_items > 0 else 0.0

        recommended_activities = [
            {
                "id": "rec-routine-caregiver",
                "title": "Morning Sunshine Routine",
                "status": f"{completed_routine_steps}/{total_routine_steps} steps completed",
                "type": "routine",
                "icon": "🌅",
            },
            {
                "id": "rec-tasks-caregiver",
                "title": "Visual Living Tasks",
                "status": f"{completed_tasks_count}/{total_tasks_count} tasks completed",
                "type": "task",
                "icon": "📋",
            },
            {
                "id": "rec-stories-caregiver",
                "title": "Social & Emotional Topics",
                "status": f"{completed_topics_count}/{total_topics_count} modules finished",
                "type": "topic",
                "icon": "📖",
            }
        ]

        summary_stats = {
            "total_routine_steps": total_routine_steps,
            "completed_routine_steps": completed_routine_steps,
            "total_tasks": total_tasks_count,
            "completed_tasks": completed_tasks_count,
            "in_progress_tasks": len(in_progress_tasks),
            "active_reminders": len(active_reminders),
            "topics_count": total_topics_count,
            "completed_topics": completed_topics_count,
            "streak_days": max((r.streak_days or 0 for r in routines), default=0),
        }

        return CaregiverLearningReviewResponse(
            child_id=child.id,
            child_name=child_name,
            caregiver_id=current_user.id,
            is_emergency_mode=is_emg_active,
            emergency_status=emg_status,
            completed_tasks=[TaskResponse.model_validate(t) for t in completed_tasks],
            in_progress_tasks=[TaskResponse.model_validate(t) for t in in_progress_tasks],
            routines=[RoutineResponse.model_validate(r) for r in routines],
            active_reminders=[ReminderResponse.model_validate(rem) for rem in active_reminders],
            learning_topics=[LearningTopicResponse.model_validate(top) for top in topics],
            recommended_activities=recommended_activities,
            overall_completion_rate=overall_rate,
            summary_stats=summary_stats,
        )

