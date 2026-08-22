from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver
from app.domains.caregivers.schemas import CommunityCaregiverProfileSchema

def get_community_caregiver_profile(db: Session, target_user_id: str) -> CommunityCaregiverProfileSchema:
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_44_NOT_FOUND if hasattr(status, 'HTTP_44_NOT_FOUND') else status.HTTP_404_NOT_FOUND,
            detail="Caregiver user not found."
        )
    
    caregiver = db.query(Caregiver).filter(Caregiver.user_id == user.id).first()
    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver profile not found."
        )

    last_seen_str = caregiver.last_seen.isoformat() if caregiver.last_seen else None
    
    return CommunityCaregiverProfileSchema(
        id=caregiver.id,
        user_id=user.id,
        name=user.full_name,
        bio=caregiver.bio,
        avatar_url=caregiver.avatar_url,
        is_verified=caregiver.is_verified,
        is_online=caregiver.is_online,
        last_seen=last_seen_str,
    )

def get_caregiver_privacy_settings(db: Session, user_id: str):
    from app.domains.caregivers.models import CaregiverPrivacySettings
    settings = db.query(CaregiverPrivacySettings).filter(CaregiverPrivacySettings.user_id == user_id).first()
    if not settings:
        settings = CaregiverPrivacySettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_caregiver_privacy_settings(db: Session, user_id: str, updates):
    from app.domains.caregivers.models import CaregiverPrivacySettings
    settings = get_caregiver_privacy_settings(db, user_id)
    
    if updates.profile_visibility is not None:
        settings.profile_visibility = updates.profile_visibility
    if updates.messaging_privacy is not None:
        settings.messaging_privacy = updates.messaging_privacy
    if updates.group_privacy is not None:
        settings.group_privacy = updates.group_privacy
    if updates.notification_privacy is not None:
        settings.notification_privacy = updates.notification_privacy
        
    if updates.public_profile is not None:
        settings.public_profile = updates.public_profile
    if updates.show_location is not None:
        settings.show_location = updates.show_location
    if updates.activity_status is not None:
        settings.activity_status = updates.activity_status
    if updates.receive_direct_messages is not None:
        settings.receive_direct_messages = updates.receive_direct_messages
    if updates.filter_unknown_senders is not None:
        settings.filter_unknown_senders = updates.filter_unknown_senders
    if updates.read_receipts is not None:
        settings.read_receipts = updates.read_receipts
        
    db.commit()
    db.refresh(settings)
    return settings

def update_caregiver_profile(db: Session, user_id: str, updates):
    caregiver = db.query(Caregiver).filter(Caregiver.user_id == user_id).first()
    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver profile not found."
        )
    if updates.bio is not None:
        caregiver.bio = updates.bio
    if updates.avatar_url is not None:
        caregiver.avatar_url = updates.avatar_url
    db.commit()
    db.refresh(caregiver)
    return get_community_caregiver_profile(db, user_id)

def submit_verification_request(db: Session, user_id: str, req):
    from app.domains.caregivers.models import VerificationSubmission
    if not req.role_bio or not req.role_bio.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role bio description is required for verification."
        )

    # Check for existing pending request
    existing = db.query(VerificationSubmission).filter(
        VerificationSubmission.user_id == user_id,
        VerificationSubmission.status == "pending"
    ).first()

    if existing:
        existing.role_bio = req.role_bio
        if req.document_notes:
            existing.document_notes = req.document_notes
        db.commit()
        db.refresh(existing)
        return {
            "id": existing.id,
            "user_id": existing.user_id,
            "role_bio": existing.role_bio,
            "document_notes": existing.document_notes,
            "status": existing.status,
            "message": "Verification request updated and pending review.",
            "submitted_at": existing.submitted_at.isoformat()
        }

    sub = VerificationSubmission(
        user_id=user_id,
        role_bio=req.role_bio,
        document_notes=req.document_notes,
        status="pending"
    )
    db.add(sub)

    # Update caregiver status if pending
    cg = db.query(Caregiver).filter(Caregiver.user_id == user_id).first()
    if cg and not cg.is_verified:
        cg.verification_status = "pending"

    db.commit()
    db.refresh(sub)

    return {
        "id": sub.id,
        "user_id": sub.user_id,
        "role_bio": sub.role_bio,
        "document_notes": sub.document_notes,
        "status": sub.status,
        "message": "Caregiver verification request submitted successfully.",
        "submitted_at": sub.submitted_at.isoformat()
    }

def get_verification_submission(db: Session, user_id: str):
    from app.domains.caregivers.models import VerificationSubmission, Caregiver
    sub = db.query(VerificationSubmission).filter(
        VerificationSubmission.user_id == user_id
    ).order_by(VerificationSubmission.submitted_at.desc()).first()

    if not sub:
        cg = db.query(Caregiver).filter(Caregiver.user_id == user_id).first()
        status_val = cg.verification_status if cg else "pending"
        return {
            "id": f"sub-default-{user_id}",
            "user_id": user_id,
            "role_bio": cg.bio if cg else "Caregiver",
            "document_notes": None,
            "status": status_val,
            "message": f"Verification request status is {status_val}.",
            "submitted_at": cg.created_at.isoformat() if cg and cg.created_at else datetime.utcnow().isoformat()
        }

    return {
        "id": sub.id,
        "user_id": sub.user_id,
        "role_bio": sub.role_bio,
        "document_notes": sub.document_notes,
        "status": sub.status,
        "message": f"Verification request status is {sub.status}.",
        "submitted_at": sub.submitted_at.isoformat()
    }




