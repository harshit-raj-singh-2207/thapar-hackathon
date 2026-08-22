from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Post, Comment
from app.domains.notifications.models import Notification

router = APIRouter(tags=["Community Post Comments"])

class CreateCommentRequest(BaseModel):
    content: str

class UpdateCommentRequest(BaseModel):
    content: str

@router.get("/community/posts/{post_id}/comments")
def get_post_comments(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).order_by(Comment.created_at.asc()).all()

    results = []
    for c in comments:
        author_user = db.query(User).filter(User.id == c.author_id).first()
        author_cg = db.query(Caregiver).filter(Caregiver.user_id == c.author_id).first()
        is_verified = author_cg.is_verified if author_cg else False
        avatar_url = author_cg.avatar_url if author_cg else None

        results.append({
            "id": c.id,
            "post_id": c.post_id,
            "author_id": c.author_id,
            "author_name": author_user.full_name if author_user else "Caregiver",
            "author_avatar": avatar_url,
            "is_verified_caregiver": is_verified,
            "is_verified": is_verified,
            "author": {
                "id": c.author_id,
                "name": author_user.full_name if author_user else "Caregiver",
                "avatar_url": avatar_url,
                "is_verified": is_verified,
            },
            "content": c.content,
            "text": c.content,
            "is_own": c.author_id == user_id,
            "created_at": c.created_at.isoformat(),
            "timestamp": c.created_at.isoformat(),
        })
    return results

@router.post("/community/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: str,
    req: CreateCommentRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if not req.content or not req.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content cannot be empty.")

    user = db.query(User).filter(User.id == user_id).first()

    comment = Comment(
        post_id=post_id,
        author_id=user_id,
        content=req.content.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Recalculate post comment_count accurately from Comment table
    post.comment_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    db.commit()

    # Dispatch notification to post author if not commenting on own post
    if post.author_id != user_id:
        notif = Notification(
            user_id=post.author_id,
            type="comment",
            title="New Comment on Your Post",
            body=f"{user.full_name if user else 'A caregiver'} commented: '{comment.content[:50]}...'",
        )
        db.add(notif)
        db.commit()

        # Real-time WebSocket delivery
        from app.realtime.notification_manager import notification_manager
        await notification_manager.send_notification(post.author_id, notif)

    # Broadcast live comment stream over WebSocket to all active users
    from app.realtime.connection_manager import manager
    try:
        await manager.broadcast_all({
            "type": "new_comment",
            "post_id": post_id,
            "comment": {
                "id": comment.id,
                "post_id": comment.post_id,
                "author_id": comment.author_id,
                "author_name": user.full_name if user else "Caregiver",
                "author_avatar": caregiver.avatar_url,
                "is_verified": caregiver.is_verified,
                "content": comment.content,
                "text": comment.content,
                "created_at": comment.created_at.isoformat(),
                "timestamp": comment.created_at.isoformat(),
            }
        })
    except Exception:
        pass

    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_name": user.full_name if user else "Caregiver",
        "author_avatar": caregiver.avatar_url,
        "is_verified_caregiver": caregiver.is_verified,
        "is_verified": caregiver.is_verified,
        "author": {
            "id": comment.author_id,
            "name": user.full_name if user else "Caregiver",
            "avatar_url": caregiver.avatar_url,
            "is_verified": caregiver.is_verified,
        },
        "content": comment.content,
        "text": comment.content,
        "is_own": True,
        "created_at": comment.created_at.isoformat(),
        "timestamp": comment.created_at.isoformat(),
    }


@router.put("/community/comments/{comment_id}")
@router.put("/community/posts/{post_id}/comments/{comment_id}")
def update_comment(
    comment_id: str,
    req: UpdateCommentRequest,
    post_id: Optional[str] = None,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    if comment.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot edit another caregiver's comment."
        )

    if not req.content or not req.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content cannot be empty.")

    comment.content = req.content.strip()
    db.commit()
    db.refresh(comment)

    author_user = db.query(User).filter(User.id == comment.author_id).first()
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_name": author_user.full_name if author_user else "Caregiver",
        "is_verified_caregiver": caregiver.is_verified,
        "author": {
            "id": comment.author_id,
            "name": author_user.full_name if author_user else "Caregiver",
            "is_verified": caregiver.is_verified,
        },
        "content": comment.content,
        "text": comment.content,
        "is_own": True,
        "created_at": comment.created_at.isoformat(),
        "timestamp": comment.created_at.isoformat(),
    }

@router.delete("/community/comments/{comment_id}")
@router.delete("/community/posts/{post_id}/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    post_id: Optional[str] = None,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    if comment.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete another caregiver's comment."
        )

    parent_post_id = comment.post_id
    db.delete(comment)
    db.commit()
    
    post = db.query(Post).filter(Post.id == parent_post_id).first()
    if post:
        post.comment_count = db.query(Comment).filter(Comment.post_id == parent_post_id).count()
        db.commit()

    return {"message": "Comment deleted successfully.", "comment_id": comment_id}
