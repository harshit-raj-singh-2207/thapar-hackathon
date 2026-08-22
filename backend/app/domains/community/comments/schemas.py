from pydantic import BaseModel

class CreateCommentSchema(BaseModel):
    content: str

class CommentResponseSchema(BaseModel):
    id: str
    post_id: str
    author_id: str
    author_name: str
    content: str
    is_own: bool
    created_at: str
