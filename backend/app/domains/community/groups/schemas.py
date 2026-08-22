from typing import Optional
from pydantic import BaseModel

class CreateGroupSchema(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "General"

class GroupResponseSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    creator_id: str
    member_count: int
    is_joined: bool
    user_role: Optional[str] = None
