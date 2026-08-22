from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.caregivers.models import Caregiver
from app.domains.notifications.models import Notification

router = APIRouter(prefix="/community/notifications", tags=["Community Notifications"])

@router.get("")
def list_notifications(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    notifs = db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()

    return [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "read": n.read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifs
    ]

@router.get("/unread-count")
def get_unread_count(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).count()
    return {"count": count}


@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notif.read = True
    db.commit()

    return {
        "id": notif.id,
        "read": True,
        "message": "Notification marked as read."
    }

@router.post("/read-all")
def mark_all_read(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).update({"read": True})
    db.commit()

    return {"message": "All notifications marked as read."}
