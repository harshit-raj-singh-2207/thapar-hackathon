from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver, CaregiverBlock
from app.domains.community.models import Conversation, DirectMessage
from app.domains.notifications.models import Notification

router = APIRouter(prefix="/community/chats", tags=["One-to-One Community Chat"])

class CreateChatRequest(BaseModel):
    recipient_id: str

class SendMessageRequest(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None

def check_blocked(db: Session, user1_id: str, user2_id: str):
    block = db.query(CaregiverBlock).filter(
        or_(
            and_(CaregiverBlock.blocker_id == user1_id, CaregiverBlock.blocked_id == user2_id),
            and_(CaregiverBlock.blocker_id == user2_id, CaregiverBlock.blocked_id == user1_id),
        )
    ).first()
    if block:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Communication blocked between caregivers."
        )

@router.get("")
def list_my_chats(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    convs = db.query(Conversation).filter(
        or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id)
    ).order_by(Conversation.updated_at.desc()).all()

    results = []
    for c in convs:
        other_id = c.user2_id if c.user1_id == user_id else c.user1_id
        # Filter out if blocked
        is_blocked = db.query(CaregiverBlock).filter(
            or_(
                and_(CaregiverBlock.blocker_id == user_id, CaregiverBlock.blocked_id == other_id),
                and_(CaregiverBlock.blocker_id == other_id, CaregiverBlock.blocked_id == user_id),
            )
        ).first() is not None

        if is_blocked:
            continue

        other_user = db.query(User).filter(User.id == other_id).first()
        other_cg = db.query(Caregiver).filter(Caregiver.user_id == other_id).first()
        
        last_msg = db.query(DirectMessage).filter(
            DirectMessage.conversation_id == c.id
        ).order_by(DirectMessage.created_at.desc()).first()

        results.append({
            "id": c.id,
            "recipient_id": other_id,
            "name": other_user.full_name if other_user else "Caregiver",
            "avatar_url": other_cg.avatar_url if other_cg else None,
            "is_online": other_cg.is_online if other_cg else False,
            "last_message": last_msg.text if last_msg else None,
            "last_message_at": last_msg.created_at.isoformat() if last_msg else c.created_at.isoformat(),
        })
    return results

@router.post("", status_code=status.HTTP_201_CREATED)
def create_or_get_chat(
    req: CreateChatRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    recipient_id = req.recipient_id

    check_blocked(db, user_id, recipient_id)

    existing = db.query(Conversation).filter(
        or_(
            and_(Conversation.user1_id == user_id, Conversation.user2_id == recipient_id),
            and_(Conversation.user1_id == recipient_id, Conversation.user2_id == user_id),
        )
    ).first()

    if existing:
        return {
            "id": existing.id,
            "user1_id": existing.user1_id,
            "user2_id": existing.user2_id,
            "created_at": existing.created_at.isoformat(),
        }

    new_conv = Conversation(user1_id=user_id, user2_id=recipient_id)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    return {
        "id": new_conv.id,
        "user1_id": new_conv.user1_id,
        "user2_id": new_conv.user2_id,
        "created_at": new_conv.created_at.isoformat(),
    }

@router.get("/{chat_id}/messages")
def get_chat_messages(
    chat_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if not conv or (conv.user1_id != user_id and conv.user2_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private conversation."
        )

    other_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
    check_blocked(db, user_id, other_id)

    messages = db.query(DirectMessage).filter(
        DirectMessage.conversation_id == chat_id
    ).order_by(DirectMessage.created_at.asc()).all()

    return [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "sender_id": m.sender_id,
            "text": m.text,
            "attachment_url": m.attachment_url,
            "status": m.status or "sent",
            "is_own": m.sender_id == user_id,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]

@router.post("/{chat_id}/messages", status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    chat_id: str,
    req: SendMessageRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    from app.realtime.connection_manager import manager
    from app.realtime.notification_manager import notification_manager

    user_id = caregiver.user_id
    sender_user = db.query(User).filter(User.id == user_id).first()
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if not conv or (conv.user1_id != user_id and conv.user2_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private conversation."
        )

    recipient_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
    check_blocked(db, user_id, recipient_id)

    is_recipient_online = manager.is_user_connected(recipient_id)
    initial_status = "delivered" if is_recipient_online else "sent"

    msg = DirectMessage(
        conversation_id=chat_id,
        sender_id=user_id,
        text=req.text,
        attachment_url=req.image_url,
        status=initial_status,
    )
    db.add(msg)
    conv.updated_at = datetime.utcnow()

    # Dispatch notification to recipient
    notif = Notification(
        user_id=recipient_id,
        type="message",
        title=sender_user.full_name if sender_user else "Caregiver",
        body=req.text or "Sent an attachment",
    )
    db.add(notif)
    db.commit()
    db.refresh(msg)

    # Real-time WebSocket delivery (awaited directly in async handler)
    try:
        event_payload = {
            "type": "direct_message",
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "chat_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "sender_name": sender_user.full_name if sender_user else "Caregiver",
            "text": msg.text,
            "attachment_url": msg.attachment_url,
            "status": msg.status,
            "created_at": msg.created_at.isoformat(),
        }
        await manager.send_personal_message(event_payload, recipient_id)
        await notification_manager.send_notification(recipient_id, notif)

        if initial_status == "delivered":
            await manager.send_personal_message({
                "type": "message_delivered",
                "message_id": msg.id,
                "conversation_id": msg.conversation_id,
            }, user_id)
    except Exception:
        pass

    return {
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "sender_id": msg.sender_id,
        "text": msg.text,
        "attachment_url": msg.attachment_url,
        "status": msg.status,
        "is_own": True,
        "created_at": msg.created_at.isoformat(),
    }

@router.post("/{chat_id}/read")
async def mark_chat_messages_read(
    chat_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    from app.realtime.connection_manager import manager

    user_id = caregiver.user_id
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if not conv or (conv.user1_id != user_id and conv.user2_id != user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to private conversation."
        )

    other_id = conv.user2_id if conv.user1_id == user_id else conv.user1_id
    check_blocked(db, user_id, other_id)

    unread_msgs = db.query(DirectMessage).filter(
        DirectMessage.conversation_id == chat_id,
        DirectMessage.sender_id == other_id,
        DirectMessage.status != "read"
    ).all()

    msg_ids = [m.id for m in unread_msgs]
    if unread_msgs:
        for m in unread_msgs:
            m.status = "read"
        db.commit()

        # Notify sender that their messages have been read
        try:
            await manager.send_personal_message({
                "type": "message_read",
                "chat_id": chat_id,
                "conversation_id": chat_id,
                "reader_id": user_id,
                "message_ids": msg_ids,
            }, other_id)
        except Exception:
            pass

    return {
        "status": "ok",
        "chat_id": chat_id,
        "marked_count": len(msg_ids),
        "message_ids": msg_ids,
    }


