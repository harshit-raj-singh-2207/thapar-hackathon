from typing import List
from sqlalchemy.orm import Session
from app.domains.community.comments.repository import CommentRepository
from app.domains.community.models import Comment

class CommentService:
    def __init__(self, db: Session):
        self.repo = CommentRepository(db)

    def fetch_comments(self, post_id: str) -> List[Comment]:
        return self.repo.get_by_post(post_id)

    def add_comment(self, post_id: str, author_id: str, content: str) -> Comment:
        return self.repo.create(post_id, author_id, content)
