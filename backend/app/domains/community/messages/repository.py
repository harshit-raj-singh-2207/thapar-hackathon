from typing import List
from sqlalchemy.orm import Session
from app.domains.community.models import DirectMessage

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_conversation(self, conversation_id: str) -> List[DirectMessage]:
        return self.db.query(DirectMessage).filter(
            DirectMessage.conversation_id == conversation_id
        ).order_by(DirectMessage.created_at.asc()).all()

    def create(self, conversation_id: str, sender_id: str, text: str = None, attachment_url: str = None) -> DirectMessage:
        msg = DirectMessage(
            conversation_id=conversation_id,
            sender_id=sender_id,
            text=text,
            attachment_url=attachment_url,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg
