from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.domains.community.models import Conversation

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_users(self, user1_id: str, user2_id: str) -> Conversation:
        return self.db.query(Conversation).filter(
            or_(
                and_(Conversation.user1_id == user1_id, Conversation.user2_id == user2_id),
                and_(Conversation.user1_id == user2_id, Conversation.user2_id == user1_id),
            )
        ).first()

    def create(self, user1_id: str, user2_id: str) -> Conversation:
        conv = Conversation(user1_id=user1_id, user2_id=user2_id)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv
