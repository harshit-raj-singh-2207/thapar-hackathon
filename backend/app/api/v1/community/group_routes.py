from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.community.models import Group, GroupMember, GroupMessage

router = APIRouter(prefix="/community/groups", tags=["Caregiver Community Groups"])

class CreateGroupRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = "General"

class SendGroupMessageRequest(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None

@router.get("/discover")
def discover_groups(
    search: Optional[str] = Query(None),
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    query = db.query(Group)
    if search:
        query = query.filter(Group.name.ilike(f"%{search}%") | Group.description.ilike(f"%{search}%"))
    
    groups = query.order_by(Group.created_at.desc()).all()
    user_id = caregiver.user_id

    results = []
    for g in groups:
        member_count = db.query(GroupMember).filter(GroupMember.group_id == g.id).count()
        membership = db.query(GroupMember).filter(
            GroupMember.group_id == g.id, GroupMember.user_id == user_id
        ).first()

        results.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "category": g.category,
            "creator_id": g.creator_id,
            "avatar_url": g.avatar_url,
            "member_count": member_count,
            "is_joined": bool(membership),
            "user_role": membership.role if membership else None,
            "created_at": g.created_at.isoformat(),
        })
    return results

@router.post("", status_code=status.HTTP_201_CREATED)
def create_group(
    req: CreateGroupRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    new_group = Group(
        name=req.name,
        description=req.description,
        category=req.category,
        creator_id=user_id,
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    # Creator becomes admin member
    admin_member = GroupMember(
        group_id=new_group.id,
        user_id=user_id,
        role="admin"
    )
    db.add(admin_member)
    db.commit()

    return {
        "id": new_group.id,
        "name": new_group.name,
        "description": new_group.description,
        "category": new_group.category,
        "creator_id": new_group.creator_id,
        "member_count": 1,
        "is_joined": True,
        "user_role": "admin",
        "created_at": new_group.created_at.isoformat(),
    }

@router.post("/{group_id}/join")
def join_group(
    group_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id, GroupMember.user_id == user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this group."
        )

    new_member = GroupMember(group_id=group_id, user_id=user_id, role="member")
    db.add(new_member)
    db.commit()

    member_count = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
    return {
        "group_id": group_id,
        "is_joined": True,
        "member_count": member_count
    }

@router.post("/{group_id}/leave")
def leave_group(
    group_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id, GroupMember.user_id == user_id
    ).first()

    if membership:
        db.delete(membership)
        db.commit()

    member_count = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
    return {
        "group_id": group_id,
        "is_joined": False,
        "member_count": member_count
    }

@router.get("/{group_id}/members")
def list_group_members(
    group_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    results = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        cg = db.query(Caregiver).filter(Caregiver.user_id == m.user_id).first()
        results.append({
            "id": user.id if user else m.user_id,
            "name": user.full_name if user else "Member",
            "role": m.role,
            "is_online": cg.is_online if cg else False,
            "joined_at": m.joined_at.isoformat()
        })
    return results

@router.get("/{group_id}/messages")
def get_group_messages(
    group_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    # Check group membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id, GroupMember.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this group to view messages."
        )

    messages = db.query(GroupMessage).filter(
        GroupMessage.group_id == group_id
    ).order_by(GroupMessage.created_at.asc()).all()

    return [
        {
            "id": m.id,
            "group_id": m.group_id,
            "sender_id": m.sender_id,
            "text": m.text,
            "attachment_url": m.attachment_url,
            "is_own": m.sender_id == user_id,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]

@router.post("/{group_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_group_message(
    group_id: str,
    req: SendGroupMessageRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id, GroupMember.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a member of this group to send messages."
        )

    msg = GroupMessage(
        group_id=group_id,
        sender_id=user_id,
        text=req.text,
        attachment_url=req.image_url,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Real-time WebSocket delivery to other group members (awaited directly)
    from app.realtime.connection_manager import manager
    try:
        sender_user = db.query(User).filter(User.id == user_id).first()
        members = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id != user_id
        ).all()
        recipient_ids = [m.user_id for m in members]

        event_payload = {
            "type": "group_message",
            "id": msg.id,
            "group_id": msg.group_id,
            "sender_id": msg.sender_id,
            "sender_name": sender_user.full_name if sender_user else "Caregiver",
            "text": msg.text,
            "attachment_url": msg.attachment_url,
            "created_at": msg.created_at.isoformat(),
        }
        await manager.broadcast_to_users(event_payload, recipient_ids)
    except Exception:
        pass

    return {
        "id": msg.id,
        "group_id": msg.group_id,
        "sender_id": msg.sender_id,
        "text": msg.text,
        "attachment_url": msg.attachment_url,
        "is_own": True,
        "created_at": msg.created_at.isoformat(),
    }

