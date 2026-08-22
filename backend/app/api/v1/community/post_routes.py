from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Post, PostLike, Comment

router = APIRouter(prefix="/community/posts", tags=["Community Feed Posts"])

class CreatePostRequest(BaseModel):
    content: str
    image_url: Optional[str] = None
    category: Optional[str] = "General"

class UpdatePostRequest(BaseModel):
    content: str
    image_url: Optional[str] = None
    category: Optional[str] = None

@router.get("")
def get_posts_feed(
    category: Optional[str] = Query(None),
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    query = db.query(Post)
    if category and category != "All":
        query = query.filter(Post.category.ilike(category))

    posts = query.order_by(Post.created_at.desc()).all()
    results = []

    for p in posts:
        author_user = db.query(User).filter(User.id == p.author_id).first()
        author_cg = db.query(Caregiver).filter(Caregiver.user_id == p.author_id).first()
        is_liked = db.query(PostLike).filter(
            PostLike.post_id == p.id, PostLike.user_id == user_id
        ).first() is not None
        actual_like_count = db.query(PostLike).filter(PostLike.post_id == p.id).count()
        actual_comment_count = db.query(Comment).filter(Comment.post_id == p.id).count()
        avatar_url = author_cg.avatar_url if author_cg else None
        is_verified = author_cg.is_verified if author_cg else False

        results.append({
            "id": p.id,
            "author_id": p.author_id,
            "author_name": author_user.full_name if author_user else "Caregiver",
            "author_avatar": avatar_url,
            "is_verified_caregiver": is_verified,
            "is_verified": is_verified,
            "author": {
                "id": p.author_id,
                "name": author_user.full_name if author_user else "Caregiver",
                "avatar_url": avatar_url,
                "is_verified": is_verified,
            },
            "is_own": p.author_id == user_id,
            "content": p.content,
            "image_url": p.image_url,
            "category": p.category,
            "comment_count": actual_comment_count,
            "like_count": actual_like_count,
            "is_liked": is_liked,
            "created_at": p.created_at.isoformat(),
        })
    return results

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    req: CreatePostRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    user = db.query(User).filter(User.id == user_id).first()

    post = Post(
        author_id=user_id,
        content=req.content,
        image_url=req.image_url,
        category=req.category or "General",
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    post_dict = {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": user.full_name if user else "Caregiver",
        "author_avatar": caregiver.avatar_url,
        "is_verified_caregiver": caregiver.is_verified,
        "is_verified": caregiver.is_verified,
        "author": {
            "id": post.author_id,
            "name": user.full_name if user else "Caregiver",
            "avatar_url": caregiver.avatar_url,
            "is_verified": caregiver.is_verified,
        },
        "is_own": True,
        "content": post.content,
        "image_url": post.image_url,
        "category": post.category,
        "comment_count": 0,
        "like_count": 0,
        "is_liked": False,
        "created_at": post.created_at.isoformat(),
    }

    # Broadcast new post live over WebSocket to all active users
    from app.realtime.connection_manager import manager
    try:
        await manager.broadcast_all({
            "type": "new_post",
            "post": post_dict,
        })
    except Exception:
        pass

    return post_dict

@router.get("/{post_id}")
def get_post_details(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    author_user = db.query(User).filter(User.id == post.author_id).first()
    author_cg = db.query(Caregiver).filter(Caregiver.user_id == post.author_id).first()
    is_liked = db.query(PostLike).filter(
        PostLike.post_id == post.id, PostLike.user_id == user_id
    ).first() is not None
    actual_like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
    actual_comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
    avatar_url = author_cg.avatar_url if author_cg else None
    is_verified = author_cg.is_verified if author_cg else False

    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": author_user.full_name if author_user else "Caregiver",
        "author_avatar": avatar_url,
        "is_verified_caregiver": is_verified,
        "is_verified": is_verified,
        "author": {
            "id": post.author_id,
            "name": author_user.full_name if author_user else "Caregiver",
            "avatar_url": avatar_url,
            "is_verified": is_verified,
        },
        "is_own": post.author_id == user_id,
        "content": post.content,
        "image_url": post.image_url,
        "category": post.category,
        "comment_count": actual_comment_count,
        "like_count": actual_like_count,
        "is_liked": is_liked,
        "created_at": post.created_at.isoformat(),
    }


@router.put("/{post_id}")
def update_post(
    post_id: str,
    req: UpdatePostRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if post.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot edit another caregiver's post."
        )

    post.content = req.content
    if req.image_url is not None:
        post.image_url = req.image_url
    if req.category is not None:
        post.category = req.category

    db.commit()
    db.refresh(post)

    actual_like_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
    actual_comment_count = db.query(Comment).filter(Comment.post_id == post.id).count()
    author_user = db.query(User).filter(User.id == post.author_id).first()
    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": author_user.full_name if author_user else "Caregiver",
        "is_verified_caregiver": caregiver.is_verified,
        "author": {
            "id": post.author_id,
            "name": author_user.full_name if author_user else "Caregiver",
            "is_verified": caregiver.is_verified,
        },
        "is_own": True,
        "content": post.content,
        "image_url": post.image_url,
        "category": post.category,
        "comment_count": actual_comment_count,
        "like_count": actual_like_count,
        "created_at": post.created_at.isoformat(),
    }

@router.delete("/{post_id}")
def delete_post(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if post.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete another caregiver's post."
        )

    # Delete related likes and comments
    db.query(PostLike).filter(PostLike.post_id == post_id).delete()
    db.query(Comment).filter(Comment.post_id == post_id).delete()
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully.", "post_id": post_id}

@router.post("/{post_id}/like")
async def toggle_like_post(
    post_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    from app.domains.notifications.models import Notification
    from app.realtime.notification_manager import notification_manager

    user_id = caregiver.user_id
    user = db.query(User).filter(User.id == user_id).first()
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id, PostLike.user_id == user_id
    ).first()

    if existing_like:
        db.delete(existing_like)
        is_liked = False
        db.commit()
    else:
        new_like = PostLike(post_id=post_id, user_id=user_id)
        db.add(new_like)
        is_liked = True

        # Dispatch real-time notification to post author if not liking own post
        if post.author_id != user_id:
            notif = Notification(
                user_id=post.author_id,
                type="like",
                title="New Like on Your Post",
                body=f"{user.full_name if user else 'A caregiver'} liked your post.",
            )
            db.add(notif)
            db.commit()
            await notification_manager.send_notification(post.author_id, notif)
        else:
            db.commit()

    # Recalculate exact like count from PostLike table
    like_count = db.query(PostLike).filter(PostLike.post_id == post_id).count()
    post.like_count = like_count
    db.commit()

    return {
        "post_id": post_id,
        "like_count": like_count,
        "is_liked": is_liked
    }

