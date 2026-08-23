from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models.user import User
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
    EmergencyLearningPlanResponse,
    CaregiverLearningReviewResponse,
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

# ==============================================================================
# Emergency Learning Mode & Caregiver Remote Review APIs
# ==============================================================================

@router.get(
    "/emergency-plan",
    response_model=EmergencyLearningPlanResponse,
    summary="Get Emergency Home Learning Plan (Current User/Default Child)"
)
@router.get(
    "/emergency/plan",
    response_model=EmergencyLearningPlanResponse,
    summary="Get Emergency Home Learning Plan (Alias)"
)
def get_emergency_learning_plan_current(
    child_id: Optional[str] = Query(None, description="Optional child ID"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve unified home-based emergency learning plan for remote isolation.
    Combines structured daily routines, visual task breakdowns, hydration/sensory reminders,
    learning topics, and AI tutor Nivi recommendations.
    """
    service = LearningService(db)
    return service.get_emergency_learning_plan(child_id=child_id, current_user=current_user)

@router.get(
    "/emergency-plan/{child_id}",
    response_model=EmergencyLearningPlanResponse,
    summary="Get Emergency Home Learning Plan by Child ID"
)
@router.get(
    "/emergency/plan/{child_id}",
    response_model=EmergencyLearningPlanResponse,
    summary="Get Emergency Home Learning Plan by Child ID (Alias)"
)
def get_emergency_learning_plan_by_child(
    child_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve unified home-based emergency learning plan for a specific child.
    Validates caregiver authorization when authentication is present.
    """
    service = LearningService(db)
    return service.get_emergency_learning_plan(child_id=child_id, current_user=current_user)

@router.get(
    "/caregiver-review/{child_id}",
    response_model=CaregiverLearningReviewResponse,
    summary="Caregiver Remote Learning Review"
)
@router.get(
    "/caregiver-summary/{child_id}",
    response_model=CaregiverLearningReviewResponse,
    summary="Caregiver Remote Learning Summary (Alias)"
)
@router.get(
    "/caregiver/review/{child_id}",
    response_model=CaregiverLearningReviewResponse,
    summary="Caregiver Remote Learning Review (Nested Alias)"
)
def get_caregiver_learning_review(
    child_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caregiver remote supervision dashboard view to review child's learning progress,
    completed routines/tasks, active reminders, and AI recommended activities.
    Enforces caregiver ownership.
    """
    service = LearningService(db)
    return service.get_caregiver_learning_review(child_id=child_id, current_user=current_user)

