from typing import List
from sqlalchemy.orm import Session
from app.domains.community.models import Comment

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_post(self, post_id: str) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()

    def create(self, post_id: str, author_id: str, content: str) -> Comment:
        comment = Comment(post_id=post_id, author_id=author_id, content=content)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
