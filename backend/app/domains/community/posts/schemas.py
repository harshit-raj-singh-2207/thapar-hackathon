from typing import Optional
from pydantic import BaseModel

class CreatePostSchema(BaseModel):
    content: str
    image_url: Optional[str] = None
    category: Optional[str] = "General"

class PostResponseSchema(BaseModel):
    id: str
    author_id: str
    author_name: str
    content: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    comment_count: int
    like_count: int
    is_liked: bool
    is_own: bool
