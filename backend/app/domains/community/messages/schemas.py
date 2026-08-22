from typing import Optional
from pydantic import BaseModel

class SendMessageSchema(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None

class DirectMessageResponseSchema(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    text: Optional[str] = None
    attachment_url: Optional[str] = None
    is_own: bool
    created_at: str
