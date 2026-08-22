from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.domains.learning.repository import LearningRepository
from app.domains.learning.models import Routine, Task, Reminder, LearningTopic
from app.domains.learning.schemas import (
    RoutineCreate,
    TaskBreakdownRequest,
    TaskBreakdownResponse,
    TaskCreate,
    ReminderCreate,
    TutorAskRequest,
    TutorAskResponse,
)
from app.domains.learning.routine_service import RoutineService
from app.domains.learning.task_service import TaskService
from app.domains.learning.tutor_service import TutorService

class LearningService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LearningRepository(db)
        self.routine_service = RoutineService(db)
        self.task_service = TaskService(db)
        self.tutor_service = TutorService(db)

    # Routines
    def get_routines(self, user_id: Optional[str] = None) -> List[Routine]:
        return self.routine_service.get_all_routines(user_id=user_id)

    def get_routine_by_id(self, routine_id: str) -> Optional[Routine]:
        return self.routine_service.get_routine_by_id(routine_id)

    def create_routine(self, req: RoutineCreate, user_id: Optional[str] = None) -> Routine:
        return self.routine_service.create_routine(req, user_id=user_id)

    def toggle_routine_step(self, step_id: str):
        return self.routine_service.toggle_step(step_id)

    def reset_routine(self, routine_id: str):
        return self.routine_service.reset_routine(routine_id)

    # Tasks
    def breakdown_task_ai(self, req: TaskBreakdownRequest) -> TaskBreakdownResponse:
        return self.task_service.breakdown_task_ai(req)

    def get_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        return self.task_service.get_all_tasks(user_id=user_id)

    def create_task(self, req: TaskCreate, user_id: Optional[str] = None) -> Task:
        return self.task_service.create_task(req, user_id=user_id)

    def update_task_step_progress(self, task_id: str, step_index: int, is_completed: bool) -> Optional[Task]:
        return self.task_service.update_task_progress(task_id, step_index, is_completed)

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
