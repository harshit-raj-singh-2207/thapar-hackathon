from sqlalchemy.orm import Session
from app.domains.community.chat.service import ChatService
from app.domains.community.messages.service import MessageService
from app.domains.community.groups.service import GroupService
from app.domains.community.posts.service import PostService
from app.domains.community.comments.service import CommentService
from app.domains.community.moderation.moderation_service import ModerationService

class CommunityService:
    def __init__(self, db: Session):
        self.db = db
        self.chat = ChatService(db)
        self.messages = MessageService(db)
        self.groups = GroupService(db)
        self.posts = PostService(db)
        self.comments = CommentService(db)
        self.moderation = ModerationService(db)
