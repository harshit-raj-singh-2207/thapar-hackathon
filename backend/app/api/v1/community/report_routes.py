from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_verified_caregiver
from app.domains.caregivers.models import Caregiver, CaregiverBlock, ContentReport

router = APIRouter(prefix="/community/safety", tags=["Community Safety & Moderation"])

class ReportRequest(BaseModel):
    target_type: str  # post, comment, user, group, message
    target_id: str
    reason: str

class BlockRequest(BaseModel):
    blocked_user_id: str

@router.post("/reports", status_code=status.HTTP_201_CREATED)
def submit_report(
    req: ReportRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    if not req.target_type or not req.target_id or not req.reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_type, target_id, and reason are required."
        )

    # Duplicate check for pending report
    existing = db.query(ContentReport).filter(
        ContentReport.reporter_id == user_id,
        ContentReport.target_type == req.target_type,
        ContentReport.target_id == req.target_id,
        ContentReport.status == "pending"
    ).first()

    if existing:
        return {
            "id": existing.id,
            "target_type": existing.target_type,
            "target_id": existing.target_id,
            "reason": existing.reason,
            "status": existing.status,
            "message": "Report already submitted and under review.",
            "created_at": existing.created_at.isoformat(),
        }

    report = ContentReport(
        reporter_id=user_id,
        target_type=req.target_type,
        target_id=req.target_id,
        reason=req.reason,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": report.id,
        "target_type": report.target_type,
        "target_id": report.target_id,
        "reason": report.reason,
        "status": report.status,
        "message": "Report submitted successfully. Our safety team will review it.",
        "created_at": report.created_at.isoformat(),
    }

@router.post("/blocks", status_code=status.HTTP_201_CREATED)
def block_caregiver(
    req: BlockRequest,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    if req.blocked_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot block yourself."
        )

    existing = db.query(CaregiverBlock).filter(
        CaregiverBlock.blocker_id == user_id,
        CaregiverBlock.blocked_id == req.blocked_user_id
    ).first()

    if existing:
        return {
            "id": existing.id,
            "blocked_id": req.blocked_user_id,
            "message": "Caregiver already blocked.",
        }

    block = CaregiverBlock(
        blocker_id=user_id,
        blocked_id=req.blocked_user_id,
    )
    db.add(block)
    db.commit()
    db.refresh(block)

    return {
        "id": block.id,
        "blocked_id": req.blocked_user_id,
        "message": "Caregiver blocked successfully.",
    }

@router.post("/unblock")
@router.delete("/blocks/{blocked_user_id}")
def unblock_caregiver(
    blocked_user_id: str,
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    block = db.query(CaregiverBlock).filter(
        CaregiverBlock.blocker_id == user_id,
        CaregiverBlock.blocked_id == blocked_user_id
    ).first()

    if block:
        db.delete(block)
        db.commit()

    return {
        "blocked_id": blocked_user_id,
        "message": "Caregiver unblocked successfully."
    }

@router.get("/blocks")
def list_blocked_caregivers(
    caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    user_id = caregiver.user_id
    blocks = db.query(CaregiverBlock).filter(CaregiverBlock.blocker_id == user_id).all()
    return [{"blocked_id": b.blocked_id, "created_at": b.created_at.isoformat()} for b in blocks]
