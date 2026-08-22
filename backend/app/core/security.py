import jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback simple match if seeded plain text
        return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

from typing import Optional, Union

def create_access_token(user_id_or_data: Union[str, dict], expires_delta: Optional[timedelta] = None) -> str:
    if isinstance(user_id_or_data, dict):
        user_id = user_id_or_data.get("sub") or user_id_or_data.get("user_id") or str(user_id_or_data)
    else:
        user_id = str(user_id_or_data)

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if isinstance(sub, dict):
            return sub.get("sub") or sub.get("user_id")
        return sub
    except Exception:
        return None

