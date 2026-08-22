from sqlalchemy.orm import Session
from app.domains.community.posts.repository import PostRepository
from app.domains.community.models import Post

class PostService:
    def __init__(self, db: Session):
        self.repo = PostRepository(db)

    def create_post(self, author_id: str, content: str, image_url: str = None, category: str = "General") -> Post:
        return self.repo.create(author_id, content, image_url, category)
