from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.domains.users.models import User
from app.domains.caregivers.models import Caregiver

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str
    is_verified: bool
    verification_status: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    bio: str = "Parent caregiver"

class ForgotPasswordRequest(BaseModel):
    email: str

class MessageResponse(BaseModel):
    message: str

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    if not email_clean or not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required.",
        )

    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    
    caregiver = db.query(Caregiver).filter(Caregiver.user_id == user.id).first()
    is_verified = caregiver.is_verified if caregiver else False
    verification_status = caregiver.verification_status if caregiver else "pending"

    token = create_access_token(user.id)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_verified=is_verified,
        verification_status=verification_status,
    )

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    full_name_clean = req.full_name.strip()
    
    if not email_clean or "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address.",
        )
    if not full_name_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name is required.",
        )
    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters.",
        )

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )
    
    new_user = User(
        email=email_clean,
        hashed_password=get_password_hash(req.password),
        full_name=full_name_clean,
        role="caregiver",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_caregiver = Caregiver(
        user_id=new_user.id,
        bio=req.bio,
        is_verified=True,  # Default verified for testing & community onboarding
        verification_status="verified",
        is_online=True,
    )
    db.add(new_caregiver)
    db.commit()
    db.refresh(new_caregiver)

    token = create_access_token(new_user.id)
    return TokenResponse(
        access_token=token,
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_verified=new_caregiver.is_verified,
        verification_status=new_caregiver.verification_status,
    )

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address.",
        )
    user = db.query(User).filter(User.email == email_clean).first()
    # Always return success message to prevent user enumeration
    return MessageResponse(
        message="If an account exists with this email, instructions have been sent."
    )
