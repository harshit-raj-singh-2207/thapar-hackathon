from typing import List, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.realtime.connection_manager import manager

router = APIRouter(tags=["Social Section & Likes"])

# In-Memory Database Simulation for interactive social section
social_db = {
    "likes": 0,
    "comments": [
        {"id": 1, "text": "First comment! Love this post."},
        {"id": 2, "text": "Awesome architecture stack."}
    ]
}

# Data Models
class CommentCreate(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: int
    text: str

class PostStateResponse(BaseModel):
    likes: int
    comments: List[CommentResponse]

# --- Endpoints ---

@router.get("/post-state", response_model=PostStateResponse)
@router.get("/api/post-state", response_model=PostStateResponse)
def get_post_state():
    """Fetches the current count of likes and all comments."""
    return social_db

@router.post("/like", response_model=Dict[str, int])
@router.post("/api/like", response_model=Dict[str, int])
async def toggle_like():
    """Increments the absolute like count and broadcasts real-time sound event."""
    social_db["likes"] += 1

    # Broadcast like event with sound metadata over WebSocket
    try:
        await manager.broadcast_all({
            "type": "social_like",
            "likes": social_db["likes"],
            "sound": "like",
            "sound_url": "/api/sounds/like",
        })
    except Exception:
        pass

    return {"likes": social_db["likes"]}

@router.post("/comment", response_model=CommentResponse)
@router.post("/api/comment", response_model=CommentResponse)
async def add_comment(comment: CommentCreate):
    """Appends a new string comment to the post array and broadcasts real-time sound event."""
    if not comment.text or not comment.text.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    new_id = len(social_db["comments"]) + 1
    new_comment = {"id": new_id, "text": comment.text.strip()}
    social_db["comments"].append(new_comment)

    # Broadcast comment event with sound metadata over WebSocket
    try:
        await manager.broadcast_all({
            "type": "social_comment",
            "comment": new_comment,
            "sound": "comment",
            "sound_url": "/api/sounds/comment",
        })
    except Exception:
        pass

    return new_comment
