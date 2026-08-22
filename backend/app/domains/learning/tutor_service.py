from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.domains.learning.repository import LearningRepository
from app.domains.learning.schemas import TutorAskRequest, TutorAskResponse
from app.ai.learning_ai import LearningAI

class TutorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LearningRepository(db)

    def ask_tutor(self, req: TutorAskRequest, user_id: Optional[str] = None) -> TutorAskResponse:
        session = self.repo.get_or_create_tutor_session(session_id=req.session_id, user_id=user_id)
        
        # Call AI Tutor reasoning
        ai_res = LearningAI.answer_tutor_question(req.question)

        # Log conversation turns
        self.repo.append_tutor_message(session.id, {
            "sender": "child",
            "text": req.question,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.repo.append_tutor_message(session.id, {
            "sender": "tutor",
            "text": ai_res["reply"],
            "simple_analogy": ai_res.get("simple_analogy"),
            "follow_up_questions": ai_res.get("follow_up_questions", []),
            "icon": ai_res.get("icon", "💡"),
            "timestamp": datetime.utcnow().isoformat(),
        })

        return TutorAskResponse(
            session_id=session.id,
            question=req.question,
            reply=ai_res["reply"],
            simple_analogy=ai_res.get("simple_analogy"),
            follow_up_questions=ai_res.get("follow_up_questions", []),
            icon=ai_res.get("icon", "💡"),
        )
