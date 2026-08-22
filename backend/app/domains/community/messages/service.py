from typing import List
from sqlalchemy.orm import Session
from app.domains.community.messages.repository import MessageRepository
from app.domains.community.models import DirectMessage

class MessageService:
    def __init__(self, db: Session):
        self.repo = MessageRepository(db)

    def fetch_messages(self, conversation_id: str) -> List[DirectMessage]:
        return self.repo.get_by_conversation(conversation_id)

    def send_message(self, conversation_id: str, sender_id: str, text: str = None, attachment_url: str = None) -> DirectMessage:
        return self.repo.create(conversation_id, sender_id, text, attachment_url)
