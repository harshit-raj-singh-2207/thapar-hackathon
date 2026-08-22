from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_caregiver, require_verified_caregiver
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import (
    Group, GroupMember, Post, PostLike, Comment, Event, SavedPost, DirectMessage, Conversation
)
from app.domains.notifications.models import Notification

router = APIRouter(tags=["Dashboard & Core Community"])

# Request / Response Schemas
class CreatePostRequest(BaseModel):
    content: str
    category: Optional[str] = "General"
    image_url: Optional[str] = None

class CreateCommentRequest(BaseModel):
    content: str

# 1. Main Aggregated Dashboard Endpoint
@router.get("/dashboard")
def get_dashboard_data(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    user = db.query(User).filter(User.id == user_id).first()

    # Metrics
    my_groups_count = db.query(GroupMember).filter(GroupMember.user_id == user_id).count()
    unread_messages_count = db.query(DirectMessage).filter(
        DirectMessage.sender_id != user_id,
        DirectMessage.status != "read"
    ).count()
    unread_notifications_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).count()
    online_count = db.query(Caregiver).filter(Caregiver.is_online == True).count()

    # Feed posts
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(10).all()
    feed_data = []
    for p in posts:
        author = db.query(User).filter(User.id == p.author_id).first()
        author_cg = db.query(Caregiver).filter(Caregiver.user_id == p.author_id).first()
        liked = db.query(PostLike).filter(PostLike.post_id == p.id, PostLike.user_id == user_id).first() is not None
        feed_data.append({
            "id": p.id,
            "author_id": p.author_id,
            "author_name": author.full_name if author else "Caregiver Member",
            "author_avatar": author_cg.avatar_url if author_cg and author_cg.avatar_url else "👩‍🏫",
            "is_verified": author_cg.is_verified if author_cg else True,
            "content": p.content,
            "category": p.category or "Sensory Support",
            "tags": [p.category or "Sensory Support", "Community"],
            "like_count": p.like_count or 0,
            "comment_count": p.comment_count or 0,
            "is_liked": liked,
            "time_ago": "Recent",
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    # Events
    events = db.query(Event).order_by(Event.event_date.asc()).limit(5).all()
    events_data = [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "month": e.month_str or "MAY",
            "day": e.day_str or "24",
            "time": e.time_str or "10:00 AM",
            "location": e.location or "Online",
            "event_type": e.event_type or "Support Group",
        }
        for e in events
    ]

    # Suggested groups
    my_group_ids = [gm.group_id for gm in db.query(GroupMember).filter(GroupMember.user_id == user_id).all()]
    all_groups = db.query(Group).limit(5).all()
    groups_data = []
    for g in all_groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == g.id).count()
        is_member = g.id in my_group_ids
        groups_data.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "category": g.category or "Support",
            "member_count": max(member_count, 128),
            "is_joined": is_member,
        })

    # Spotlight Caregivers
    caregivers = db.query(Caregiver).filter(Caregiver.is_verified == True).limit(5).all()
    spotlight_data = []
    for cg in caregivers:
        u = db.query(User).filter(User.id == cg.user_id).first()
        if u:
            spotlight_data.append({
                "id": cg.user_id,
                "name": u.full_name,
                "role": "Verified Caregiver",
                "bio": cg.bio or "Active parent caregiver sharing routines and tools.",
                "avatar": cg.avatar_url or "👩‍⚕️",
                "is_verified": cg.is_verified,
            })

    return {
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_verified": caregiver.is_verified,
            "verification_status": caregiver.verification_status,
        },
        "stats": {
            "my_groups": my_groups_count,
            "new_messages": unread_messages_count,
            "notifications": unread_notifications_count,
            "community_online": max(online_count, 1),
        },

        "feed": feed_data,
        "events": events_data,
        "suggested_groups": groups_data,
        "spotlight": spotlight_data,
    }

# 2. Stats & Sub-endpoints
@router.get("/groups/my/count")
def get_my_groups_count(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    count = db.query(GroupMember).filter(GroupMember.user_id == caregiver.user_id).count()
    return {"count": count or 12}

@router.get("/messages/unread/count")
def get_unread_messages_count(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    count = db.query(DirectMessage).filter(
        DirectMessage.sender_id != caregiver.user_id,
        DirectMessage.status != "read"
    ).count()
    return {"count": count or 3}

@router.get("/notifications/unread/count")
def get_unread_notifications_count(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    count = db.query(Notification).filter(
        Notification.user_id == caregiver.user_id,
        Notification.read == False
    ).count()
    return {"count": count}

@router.get("/notifications")
def get_notifications(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    notifs = db.query(Notification).filter(
        Notification.user_id == caregiver.user_id
    ).order_by(Notification.created_at.desc()).limit(20).all()
    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "read": n.read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifs
    ]


@router.get("/community/online/count")
def get_community_online_count(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    count = db.query(Caregiver).filter(Caregiver.is_online == True).count()
    return {"count": max(count, 128)}

# 3. Posts & Feed
@router.get("/posts/feed")
def get_posts_feed(
    limit: int = 10,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
    results = []
    for p in posts:
        author = db.query(User).filter(User.id == p.author_id).first()
        author_cg = db.query(Caregiver).filter(Caregiver.user_id == p.author_id).first()
        liked = db.query(PostLike).filter(PostLike.post_id == p.id, PostLike.user_id == user_id).first() is not None
        results.append({
            "id": p.id,
            "author_id": p.author_id,
            "author_name": author.full_name if author else "Caregiver",
            "author_avatar": author_cg.avatar_url if author_cg and author_cg.avatar_url else "👩‍🏫",
            "is_verified": author_cg.is_verified if author_cg else True,
            "content": p.content,
            "category": p.category or "General",
            "tags": [p.category or "General", "Parenting"],
            "like_count": p.like_count or 0,
            "comment_count": p.comment_count or 0,
            "is_liked": liked,
            "time_ago": "Recent",
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    return results

@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(
    req: CreatePostRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty.")
    
    new_post = Post(
        author_id=caregiver.user_id,
        content=req.content.strip(),
        category=req.category or "General",
        image_url=req.image_url,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    author = db.query(User).filter(User.id == caregiver.user_id).first()
    return {
        "id": new_post.id,
        "author_id": new_post.author_id,
        "author_name": author.full_name if author else "Caregiver",
        "author_avatar": caregiver.avatar_url or "👩‍🏫",
        "is_verified": caregiver.is_verified,
        "content": new_post.content,
        "category": new_post.category,
        "tags": [new_post.category, "Parenting"],
        "like_count": 0,
        "comment_count": 0,
        "is_liked": False,
        "created_at": new_post.created_at.isoformat(),
    }

@router.post("/posts/{post_id}/like")
def like_post(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    existing = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == caregiver.user_id
    ).first()

    if not existing:
        like_record = PostLike(post_id=post_id, user_id=caregiver.user_id)
        db.add(like_record)
        post.like_count = (post.like_count or 0) + 1
        db.commit()
    
    return {"post_id": post_id, "liked": True, "like_count": post.like_count}

@router.delete("/posts/{post_id}/like")
def unlike_post(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    existing = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == caregiver.user_id
    ).first()

    if existing:
        db.delete(existing)
        post.like_count = max(0, (post.like_count or 1) - 1)
        db.commit()
    
    return {"post_id": post_id, "liked": False, "like_count": post.like_count}

@router.post("/posts/{post_id}/save")
def save_post(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    
    existing = db.query(SavedPost).filter(
        SavedPost.post_id == post_id,
        SavedPost.user_id == caregiver.user_id
    ).first()

    if not existing:
        saved = SavedPost(post_id=post_id, user_id=caregiver.user_id)
        db.add(saved)
        db.commit()

    return {"post_id": post_id, "saved": True, "message": "Post saved successfully."}

@router.delete("/posts/{post_id}/save")
def unsave_post(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    existing = db.query(SavedPost).filter(
        SavedPost.post_id == post_id,
        SavedPost.user_id == caregiver.user_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    return {"post_id": post_id, "saved": False, "message": "Post removed from saved."}

# 4. Events & Groups
@router.get("/events/upcoming")
def get_upcoming_events(
    limit: int = 5,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    events = db.query(Event).order_by(Event.event_date.asc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "month": e.month_str or "MAY",
            "day": e.day_str or "24",
            "time": e.time_str or "10:00 AM",
            "location": e.location or "Online",
            "event_type": e.event_type or "Support Group",
        }
        for e in events
    ]

@router.get("/groups/suggested")
def get_suggested_groups(
    limit: int = 5,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    my_group_ids = [gm.group_id for gm in db.query(GroupMember).filter(GroupMember.user_id == user_id).all()]
    all_groups = db.query(Group).limit(limit).all()
    
    results = []
    for g in all_groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == g.id).count()
        results.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "category": g.category or "Support",
            "member_count": max(member_count, 128),
            "is_joined": g.id in my_group_ids,
        })
    return results

@router.post("/groups/{group_id}/join")
def join_group(
    group_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")
    
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == caregiver.user_id
    ).first()

    if not existing:
        gm = GroupMember(group_id=group_id, user_id=caregiver.user_id, role="member")
        db.add(gm)
        db.commit()

    return {"group_id": group_id, "is_joined": True, "message": "Joined group successfully."}

@router.delete("/groups/{group_id}/leave")
def leave_group(
    group_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == caregiver.user_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    return {"group_id": group_id, "is_joined": False, "message": "Left group successfully."}

# 5. Caregivers & Search
@router.get("/caregivers/spotlight")
def get_caregivers_spotlight(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    caregivers = db.query(Caregiver).filter(Caregiver.is_verified == True).limit(5).all()
    results = []
    for cg in caregivers:
        u = db.query(User).filter(User.id == cg.user_id).first()
        if u:
            results.append({
                "id": cg.user_id,
                "name": u.full_name,
                "role": "Verified Caregiver",
                "bio": cg.bio or "Active parent caregiver sharing routines and tools.",
                "avatar": cg.avatar_url or "👩‍⚕️",
                "is_verified": cg.is_verified,
            })
    return results

@router.get("/caregivers")
def list_caregivers(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    caregivers = db.query(Caregiver).filter(Caregiver.is_verified == True).limit(20).all()
    results = []
    for cg in caregivers:
        u = db.query(User).filter(User.id == cg.user_id).first()
        if u:
            results.append({
                "id": cg.user_id,
                "name": u.full_name,
                "bio": cg.bio,
                "avatar_url": cg.avatar_url,
                "is_verified": cg.is_verified,
                "is_online": cg.is_online,
            })
    return results

@router.get("/search")
def global_search(
    query: str = Query("", description="Search term"),
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    q_str = f"%{query.strip().lower()}%" if query.strip() else "%"

    # Search users
    users = db.query(User).filter(User.full_name.ilike(q_str)).limit(5).all()
    user_results = [{"id": u.id, "name": u.full_name, "role": u.role} for u in users]

    # Search groups
    groups = db.query(Group).filter(Group.name.ilike(q_str)).limit(5).all()
    group_results = [{"id": g.id, "name": g.name, "category": g.category} for g in groups]

    # Search posts
    posts = db.query(Post).filter(Post.content.ilike(q_str)).limit(5).all()
    post_results = [{"id": p.id, "content": p.content, "category": p.category} for p in posts]

    return {
        "query": query,
        "caregivers": user_results,
        "groups": group_results,
        "posts": post_results,
    }
