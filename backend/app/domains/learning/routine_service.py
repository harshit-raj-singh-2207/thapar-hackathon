from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.domains.learning.repository import LearningRepository
from app.domains.learning.models import Routine, RoutineStep
from app.domains.learning.schemas import RoutineCreate

class RoutineService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LearningRepository(db)

    def get_all_routines(self, user_id: Optional[str] = None) -> List[Routine]:
        return self.repo.get_routines(user_id=user_id)

    def get_routine_by_id(self, routine_id: str) -> Optional[Routine]:
        return self.repo.get_routine_by_id(routine_id)

    def create_routine(self, req: RoutineCreate, user_id: Optional[str] = None) -> Routine:
        routine = Routine(
            user_id=user_id,
            title=req.title,
            time_of_day=req.time_of_day,
            icon=req.icon,
            color=req.color,
            is_active=req.is_active,
        )
        saved = self.repo.create_routine(routine)

        for step_data in req.steps:
            step = RoutineStep(
                routine_id=saved.id,
                step_number=step_data.step_number,
                title=step_data.title,
                instruction=step_data.instruction,
                icon=step_data.icon,
                duration_sec=step_data.duration_sec,
                is_completed=step_data.is_completed,
            )
            self.db.add(step)
        self.db.commit()
        self.db.refresh(saved)
        return saved

    def toggle_step(self, step_id: str) -> Optional[RoutineStep]:
        step = self.repo.toggle_step_completion(step_id)
        if step:
            # Check if all steps in routine are completed
            routine = self.repo.get_routine_by_id(step.routine_id)
            if routine and routine.steps:
                all_done = all(s.is_completed for s in routine.steps)
                if all_done:
                    routine.streak_days = (routine.streak_days or 0) + 1
                    self.db.commit()
        return step

    def reset_routine(self, routine_id: str) -> Optional[Routine]:
        return self.repo.reset_routine_steps(routine_id)
