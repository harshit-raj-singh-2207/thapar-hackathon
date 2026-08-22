from typing import List, Optional
from sqlalchemy.orm import Session
from app.domains.learning.models import Routine, RoutineStep, Task, Reminder, TutorChatSession, LearningTopic

class LearningRepository:
    def __init__(self, db: Session):
        self.db = db

    # Routines
    def get_routines(self, user_id: Optional[str] = None) -> List[Routine]:
        query = self.db.query(Routine)
        if user_id:
            query = query.filter((Routine.user_id == user_id) | (Routine.user_id == None))
        return query.order_by(Routine.created_at.asc()).all()

    def get_routine_by_id(self, routine_id: str) -> Optional[Routine]:
        return self.db.query(Routine).filter(Routine.id == routine_id).first()

    def create_routine(self, routine: Routine) -> Routine:
        self.db.add(routine)
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def toggle_step_completion(self, step_id: str) -> Optional[RoutineStep]:
        step = self.db.query(RoutineStep).filter(RoutineStep.id == step_id).first()
        if step:
            step.is_completed = not step.is_completed
            self.db.commit()
            self.db.refresh(step)
        return step

    def reset_routine_steps(self, routine_id: str) -> Optional[Routine]:
        routine = self.get_routine_by_id(routine_id)
        if routine:
            for s in routine.steps:
                s.is_completed = False
            self.db.commit()
            self.db.refresh(routine)
        return routine

    # Tasks
    def get_tasks(self, user_id: Optional[str] = None) -> List[Task]:
        query = self.db.query(Task)
        if user_id:
            query = query.filter((Task.user_id == user_id) | (Task.user_id == None))
        return query.order_by(Task.created_at.desc()).all()

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def create_task(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_progress(self, task_id: str, steps_data: list, is_completed: bool) -> Optional[Task]:
        task = self.get_task_by_id(task_id)
        if task:
            task.steps_data = steps_data
            task.is_completed = is_completed
            self.db.commit()
            self.db.refresh(task)
        return task

    # Reminders
    def get_reminders(self, user_id: Optional[str] = None) -> List[Reminder]:
        query = self.db.query(Reminder)
        if user_id:
            query = query.filter((Reminder.user_id == user_id) | (Reminder.user_id == None))
        return query.order_by(Reminder.created_at.asc()).all()

    def create_reminder(self, reminder: Reminder) -> Reminder:
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def toggle_reminder(self, reminder_id: str) -> Optional[Reminder]:
        rem = self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if rem:
            rem.is_active = not rem.is_active
            self.db.commit()
            self.db.refresh(rem)
        return rem

    # AI Tutor Sessions
    def get_or_create_tutor_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> TutorChatSession:
        if session_id:
            session = self.db.query(TutorChatSession).filter(TutorChatSession.id == session_id).first()
            if session:
                return session
        
        session = TutorChatSession(user_id=user_id, messages=[])
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def append_tutor_message(self, session_id: str, msg: dict):
        session = self.db.query(TutorChatSession).filter(TutorChatSession.id == session_id).first()
        if session:
            msgs = list(session.messages or [])
            msgs.append(msg)
            session.messages = msgs
            self.db.commit()

    # Topics
    def get_topics(self) -> List[LearningTopic]:
        return self.db.query(LearningTopic).order_by(LearningTopic.created_at.asc()).all()

    def get_topic_by_id(self, topic_id: str) -> Optional[LearningTopic]:
        return self.db.query(LearningTopic).filter(LearningTopic.id == topic_id).first()

    def create_topic(self, topic: LearningTopic) -> LearningTopic:
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def update_topic_progress(self, topic_id: str, progress_pct: int, is_completed: bool) -> Optional[LearningTopic]:
        topic = self.get_topic_by_id(topic_id)
        if topic:
            topic.progress_pct = progress_pct
            topic.is_completed = is_completed
            self.db.commit()
            self.db.refresh(topic)
        return topic
