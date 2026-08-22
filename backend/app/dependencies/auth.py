from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.config.security import decode_access_token
from app.models.user import User, Caregiver

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token in Authorization header."
        )
    token = authorization.split(" ")[1]
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
    return user

def get_current_caregiver(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Caregiver:
    caregiver = db.query(Caregiver).filter(Caregiver.user_id == user.id).first()
    if not caregiver:
        # Create a default caregiver profile if not already present
        caregiver = Caregiver(
            user_id=user.id,
            bio="Parent caregiver",
            is_verified=True,
            verification_status="verified",
            is_online=True,
        )
        db.add(caregiver)
        db.commit()
        db.refresh(caregiver)
    return caregiver

def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        user_id = decode_access_token(token)
        if not user_id:
            return None
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None
