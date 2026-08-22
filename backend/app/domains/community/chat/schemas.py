from typing import Optional, List
from pydantic import BaseModel

class CreateChatSchema(BaseModel):
    recipient_id: str

class ChatResponseSchema(BaseModel):
    id: str
    recipient_id: str
    name: str
    avatar_url: Optional[str] = None
    is_online: bool = False
    last_message: Optional[str] = None
    last_message_at: Optional[str] = None
