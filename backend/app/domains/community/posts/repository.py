from typing import List, Optional
from sqlalchemy.orm import Session
from app.domains.community.models import Post

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, post_id: str) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def create(self, author_id: str, content: str, image_url: str = None, category: str = "General") -> Post:
        post = Post(author_id=author_id, content=content, image_url=image_url, category=category)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
