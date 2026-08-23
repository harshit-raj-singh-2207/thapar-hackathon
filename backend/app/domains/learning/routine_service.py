from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.domains.learning.repository import LearningRepository
from app.domains.learning.models import Routine, RoutineStep
from app.domains.learning.schemas import RoutineCreate
from fastapi import HTTPException, status
from app.domains.users.models import User

class RoutineService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LearningRepository(db)

    def get_all_routines(self, user_id: Optional[str] = None) -> List[Routine]:
        return self.repo.get_routines(user_id=user_id)

    def _authorize(self, routine: Routine, user_id: str, edit: bool = False) -> None:
        if routine.user_id is None or routine.user_id == user_id:
            return
        share = self.repo.get_routine_share(routine.id, user_id)
        if share and (not edit or share.can_edit):
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this routine.")

    def get_routine_by_id(self, routine_id: str, user_id: Optional[str] = None) -> Optional[Routine]:
        routine = self.repo.get_routine_by_id(routine_id)
        if routine and user_id:
            self._authorize(routine, user_id)
        return routine

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

    def toggle_step(self, step_id: str, user_id: Optional[str] = None) -> Optional[RoutineStep]:
        existing_step = self.repo.get_step_by_id(step_id)
        if existing_step and user_id:
            routine = self.repo.get_routine_by_id(existing_step.routine_id)
            if routine:
                self._authorize(routine, user_id, edit=True)
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

    def reset_routine(self, routine_id: str, user_id: Optional[str] = None) -> Optional[Routine]:
        routine = self.repo.get_routine_by_id(routine_id)
        if routine and user_id:
            self._authorize(routine, user_id, edit=True)
        return self.repo.reset_routine_steps(routine_id)

    def share_routine(self, routine_id: str, owner_user_id: str, caregiver_user_id: str, can_edit: bool):
        routine = self.repo.get_routine_by_id(routine_id)
        if not routine:
            raise HTTPException(status_code=404, detail="Routine not found")
        if routine.user_id != owner_user_id:
            raise HTTPException(status_code=403, detail="Only the routine owner can share it.")
        caregiver = self.db.query(User).filter(User.id == caregiver_user_id).first()
        if caregiver is None:
            raise HTTPException(status_code=404, detail="Caregiver user not found")
        return self.repo.share_routine(routine_id, caregiver_user_id, can_edit)
