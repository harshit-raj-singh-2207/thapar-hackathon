from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.domains.learning.repository import LearningRepository
from app.domains.learning.models import Task
from app.domains.learning.schemas import TaskBreakdownRequest, TaskBreakdownResponse, TaskCreate
from app.ai.learning_ai import LearningAI

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LearningRepository(db)

    def breakdown_task_ai(self, req: TaskBreakdownRequest) -> TaskBreakdownResponse:
        steps = LearningAI.breakdown_task(req.task_title)
        total_duration = sum(s.get("duration_sec", 60) for s in steps)
        
        return TaskBreakdownResponse(
            task_title=req.task_title,
            steps=steps,
            total_estimated_duration_sec=total_duration,
            encouragement="You can do this! Take it one easy step at a time. ⭐",
        )

    def get_all_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        return self.repo.get_tasks(user_id=user_id)

    def create_task(self, req: TaskCreate, user_id: Optional[str] = None) -> Task:
        task = Task(
            user_id=user_id,
            title=req.title,
            description=req.description,
            category=req.category,
            icon=req.icon,
            is_completed=False,
            steps_data=req.steps_data,
        )
        return self.repo.create_task(task)

    def update_task_progress(self, task_id: str, step_index: int, is_completed: bool) -> Optional[Task]:
        task = self.repo.get_task_by_id(task_id)
        if not task:
            return None
        
        steps = list(task.steps_data or [])
        if 0 <= step_index < len(steps):
            steps[step_index]["is_completed"] = is_completed
        
        all_completed = len(steps) > 0 and all(s.get("is_completed", False) for s in steps)
        return self.repo.update_task_progress(task_id, steps, all_completed)
