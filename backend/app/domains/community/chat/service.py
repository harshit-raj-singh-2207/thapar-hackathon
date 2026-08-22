from sqlalchemy.orm import Session
from app.domains.community.chat.repository import ChatRepository
from app.domains.community.models import Conversation

class ChatService:
    def __init__(self, db: Session):
        self.repo = ChatRepository(db)

    def get_or_create_conversation(self, user1_id: str, user2_id: str) -> Conversation:
        existing = self.repo.get_by_users(user1_id, user2_id)
        if existing:
            return existing
        return self.repo.create(user1_id, user2_id)
