from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.learning.service import LearningService
from app.domains.learning.schemas import (
    RoutineResponse,
    RoutineCreate,
    TaskBreakdownRequest,
    TaskBreakdownResponse,
    TaskResponse,
    TaskCreate,
    ReminderResponse,
    ReminderCreate,
    TutorAskRequest,
    TutorAskResponse,
    LearningTopicResponse,
)

router = APIRouter(prefix="/learning", tags=["Learning & Routines"])

# Routines
@router.get("/routines", response_model=List[RoutineResponse])
def get_routines(db: Session = Depends(get_db)):
    """Get all daily routines and visual checklists."""
    service = LearningService(db)
    return service.get_routines()

@router.post("/routines", response_model=RoutineResponse)
def create_routine(req: RoutineCreate, db: Session = Depends(get_db)):
    """Create a new customized routine."""
    service = LearningService(db)
    return service.create_routine(req)

@router.post("/routines/steps/{step_id}/toggle")
def toggle_routine_step(step_id: str, db: Session = Depends(get_db)):
    """Toggle completion status of a routine step."""
    service = LearningService(db)
    step = service.toggle_routine_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return {"message": "Step toggled", "is_completed": step.is_completed}

@router.post("/routines/{routine_id}/reset")
def reset_routine(routine_id: str, db: Session = Depends(get_db)):
    """Reset all steps in a routine for the new day."""
    service = LearningService(db)
    routine = service.reset_routine(routine_id)
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    return {"message": "Routine reset successfully"}

# Task Breakdown
@router.post("/breakdown-task", response_model=TaskBreakdownResponse)
def breakdown_task(req: TaskBreakdownRequest, db: Session = Depends(get_db)):
    """AI engine breaks down any task into manageable visual micro-steps."""
    service = LearningService(db)
    return service.breakdown_task_ai(req)

@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    """Get all saved tasks with micro-step progress."""
    service = LearningService(db)
    return service.get_tasks()

@router.post("/tasks", response_model=TaskResponse)
def create_task(req: TaskCreate, db: Session = Depends(get_db)):
    """Save a broken down task to child's dashboard."""
    service = LearningService(db)
    return service.create_task(req)

@router.post("/tasks/{task_id}/steps/{step_index}")
def update_task_step(task_id: str, step_index: int, is_completed: bool, db: Session = Depends(get_db)):
    """Update checkoff status of an individual task micro-step."""
    service = LearningService(db)
    task = service.update_task_step_progress(task_id, step_index, is_completed)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task progress updated", "is_completed": task.is_completed}

# Reminders
@router.get("/reminders", response_model=List[ReminderResponse])
def get_reminders(db: Session = Depends(get_db)):
    """Get active reminders for hydration, sensory breaks, and routines."""
    service = LearningService(db)
    return service.get_reminders()

@router.post("/reminders", response_model=ReminderResponse)
def create_reminder(req: ReminderCreate, db: Session = Depends(get_db)):
    """Create a new schedule reminder."""
    service = LearningService(db)
    return service.create_reminder(req)

@router.post("/reminders/{reminder_id}/toggle")
def toggle_reminder(reminder_id: str, db: Session = Depends(get_db)):
    """Toggle a reminder on or off."""
    service = LearningService(db)
    rem = service.toggle_reminder(reminder_id)
    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder toggled", "is_active": rem.is_active}

# AI Tutor
@router.post("/tutor/ask", response_model=TutorAskResponse)
def ask_tutor(req: TutorAskRequest, db: Session = Depends(get_db)):
    """Ask AI tutor Nivi a question and receive simple, visual analogies."""
    service = LearningService(db)
    return service.ask_tutor(req)

# Topics
@router.get("/topics", response_model=List[LearningTopicResponse])
def get_learning_topics(db: Session = Depends(get_db)):
    """Get all learning topics and social stories."""
    service = LearningService(db)
    return service.get_topics()

@router.post("/topics/{topic_id}/progress")
def update_topic_progress(topic_id: str, progress_pct: int, is_completed: bool = False, db: Session = Depends(get_db)):
    """Update completion progress for a learning topic."""
    service = LearningService(db)
    topic = service.update_topic_progress(topic_id, progress_pct, is_completed)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic progress updated", "progress_pct": topic.progress_pct}
