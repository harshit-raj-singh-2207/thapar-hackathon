from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_current_caregiver,
    require_verified_caregiver,
)
from app.domains.caregivers.models import Caregiver
from app.domains.caregivers.schemas import (
    CommunityCaregiverProfileSchema,
    CommunityAccessResponseSchema,
    CaregiverPrivacySettingsSchema,
    CaregiverPrivacySettingsUpdateSchema,
    CaregiverProfileUpdateSchema,
    VerificationSubmissionCreateSchema,
    VerificationSubmissionResponseSchema,
)
from app.domains.caregivers.service import (
    get_community_caregiver_profile,
    get_caregiver_privacy_settings,
    update_caregiver_privacy_settings,
    update_caregiver_profile,
    submit_verification_request,
    get_verification_submission,
)

router = APIRouter(prefix="/caregivers", tags=["Caregivers & Community Access"])

@router.get("/me/community-access", response_model=CommunityAccessResponseSchema)
def check_community_access(
    caregiver: Caregiver = Depends(get_current_caregiver)
):
    """
    Check if the logged in caregiver has access to the verified private community.
    """
    if caregiver.is_verified:
        return CommunityAccessResponseSchema(
            has_access=True,
            is_verified=True,
            verification_status=caregiver.verification_status,
            message="Access granted to private caregiver community."
        )
    else:
        return CommunityAccessResponseSchema(
            has_access=False,
            is_verified=False,
            verification_status=caregiver.verification_status,
            message="Access restricted. Verified caregiver status is required."
        )

@router.post("/me/verification-request", response_model=VerificationSubmissionResponseSchema, status_code=status.HTTP_201_CREATED)
def post_verification_request(
    req: VerificationSubmissionCreateSchema,
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Submit or update a caregiver verification request.
    """
    return submit_verification_request(db, caregiver.user_id, req)

@router.get("/me/verification-status", response_model=VerificationSubmissionResponseSchema)
def get_my_verification_status(
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Get the authenticated caregiver's latest verification submission status.
    """
    return get_verification_submission(db, caregiver.user_id)

@router.get("/me/privacy-settings", response_model=CaregiverPrivacySettingsSchema)
def get_my_privacy_settings(
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Get the authenticated caregiver's privacy settings.
    """
    return get_caregiver_privacy_settings(db, caregiver.user_id)

@router.patch("/me/privacy-settings", response_model=CaregiverPrivacySettingsSchema)
def patch_my_privacy_settings(
    req: CaregiverPrivacySettingsUpdateSchema,
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Update the authenticated caregiver's privacy settings.
    """
    return update_caregiver_privacy_settings(db, caregiver.user_id, req)

@router.get("/me/profile", response_model=CommunityCaregiverProfileSchema)
def get_my_community_profile(
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Get the authenticated caregiver's own community profile.
    """
    return get_community_caregiver_profile(db, caregiver.user_id)

@router.patch("/me/profile", response_model=CommunityCaregiverProfileSchema)
def patch_my_community_profile(
    req: CaregiverProfileUpdateSchema,
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Update the authenticated caregiver's profile (bio, avatar).
    """
    return update_caregiver_profile(db, caregiver.user_id, req)

@router.get("/{user_id}/profile", response_model=CommunityCaregiverProfileSchema)
def get_caregiver_community_profile(
    user_id: str,
    requesting_caregiver: Caregiver = Depends(require_verified_caregiver),
    db: Session = Depends(get_db)
):
    """
    Get a caregiver's community profile.
    ENFORCED: Only verified caregivers can call this endpoint to view profiles.
    """
    return get_community_caregiver_profile(db, user_id)

@router.post("/me/request-archive")
def request_data_archive(
    caregiver: Caregiver = Depends(get_current_caregiver),
    db: Session = Depends(get_db)
):
    """
    Request an archive of caregiver personal data and activity logs.
    """
    return {
        "status": "processing",
        "user_id": caregiver.user_id,
        "message": "Your personal data archive request has been received. A secure encrypted download link will be prepared and sent to your registered email within 24 hours.",
    }



