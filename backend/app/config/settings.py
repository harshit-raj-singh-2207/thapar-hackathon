from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NIVARA Safety & Geofencing Platform"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET", "nivara-super-secret-key-caregiver-community-2026"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nivara.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Geofencing & Safety Defaults
    DEFAULT_SAFE_ZONE_RADIUS_METERS: float = 150.0
    SEPARATION_ALERT_THRESHOLD_METERS: float = 50.0
    HEARTBEAT_TIMEOUT_SECONDS: int = 120
    LOW_BATTERY_ALERT_THRESHOLD: int = 15
    GPS_ACCURACY_THRESHOLD_METERS: float = 100.0
    LOCATION_UPDATE_INTERVAL_SECONDS: int = 10
    
    # Emergency Broadcast
    EMERGENCY_BROADCAST_RETRY_COUNT: int = 3
    SMS_NOTIFICATIONS_ENABLED: bool = True
    PUSH_NOTIFICATIONS_ENABLED: bool = True

settings = Settings()
