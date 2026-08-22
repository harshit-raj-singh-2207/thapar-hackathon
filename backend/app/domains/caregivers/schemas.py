from typing import Optional
from pydantic import BaseModel

class CommunityAccessResponseSchema(BaseModel):
    has_access: bool
    is_verified: bool
    verification_status: str
    message: str

class CommunityCaregiverProfileSchema(BaseModel):
    id: str
    user_id: str
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool
    is_online: bool
    last_seen: Optional[str] = None

    class Config:
        from_attributes = True

class CaregiverPrivacySettingsSchema(BaseModel):
    user_id: str
    profile_visibility: str = "Public"
    messaging_privacy: str = "Connections Only"
    group_privacy: str = "Active"
    notification_privacy: str = "All Alerts"
    public_profile: bool = False
    show_location: bool = True
    activity_status: bool = True
    receive_direct_messages: bool = True
    filter_unknown_senders: bool = True
    read_receipts: bool = False

    class Config:
        from_attributes = True

class CaregiverPrivacySettingsUpdateSchema(BaseModel):
    profile_visibility: Optional[str] = None
    messaging_privacy: Optional[str] = None
    group_privacy: Optional[str] = None
    notification_privacy: Optional[str] = None
    public_profile: Optional[bool] = None
    show_location: Optional[bool] = None
    activity_status: Optional[bool] = None
    receive_direct_messages: Optional[bool] = None
    filter_unknown_senders: Optional[bool] = None
    read_receipts: Optional[bool] = None

class CaregiverProfileUpdateSchema(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class VerificationSubmissionCreateSchema(BaseModel):
    role_bio: str
    document_notes: Optional[str] = None

class VerificationSubmissionResponseSchema(BaseModel):
    id: str
    user_id: str
    role_bio: Optional[str] = None
    document_notes: Optional[str] = None
    status: str
    message: str
    submitted_at: str



