import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: f"chat-{uuid.uuid4().hex[:8]}")
    user1_id = Column(String, ForeignKey("users.id"), nullable=False)
    user2_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DirectMessage(Base):
    __tablename__ = "direct_messages"

    id = Column(String, primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=True)
    attachment_url = Column(String, nullable=True)
    status = Column(String, default="sent")  # sent, delivered, read
    created_at = Column(DateTime, default=datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, default=lambda: f"group-{uuid.uuid4().hex[:8]}")
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True, default="General")
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String, primary_key=True, default=lambda: f"gm-{uuid.uuid4().hex[:8]}")
    group_id = Column(String, ForeignKey("groups.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="member")  # admin, member
    joined_at = Column(DateTime, default=datetime.utcnow)

class GroupMessage(Base):
    __tablename__ = "group_messages"

    id = Column(String, primary_key=True, default=lambda: f"gmsg-{uuid.uuid4().hex[:8]}")
    group_id = Column(String, ForeignKey("groups.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=True)
    attachment_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: f"post-{uuid.uuid4().hex[:8]}")
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=True, default="General")
    comment_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(String, primary_key=True, default=lambda: f"like-{uuid.uuid4().hex[:8]}")
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=lambda: f"comment-{uuid.uuid4().hex[:8]}")
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Resource(Base):
    __tablename__ = "community_resources"

    id = Column(String, primary_key=True, default=lambda: f"res-{uuid.uuid4().hex[:8]}")
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, default="General")
    url = Column(String, nullable=True)
    file_type = Column(String, nullable=True, default="article")
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    __tablename__ = "community_events"

    id = Column(String, primary_key=True, default=lambda: f"event-{uuid.uuid4().hex[:8]}")
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_str = Column(String, nullable=True, default="10:00 AM")
    location = Column(String, nullable=True, default="Online")
    event_type = Column(String, nullable=True, default="Support Group")
    month_str = Column(String, nullable=True, default="MAY")
    day_str = Column(String, nullable=True, default="24")
    created_at = Column(DateTime, default=datetime.utcnow)

class SavedPost(Base):
    __tablename__ = "saved_posts"

    id = Column(String, primary_key=True, default=lambda: f"saved-{uuid.uuid4().hex[:8]}")
    post_id = Column(String, ForeignKey("posts.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


