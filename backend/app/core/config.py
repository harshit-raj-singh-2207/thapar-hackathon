import os
from pathlib import Path

# Automatically load .env if python-dotenv is present, or parse directly
env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file)
    except ImportError:
        # Fallback simple .env parser
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NIVARA Caregiver Community Backend")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database
    DEFAULT_DB_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "nivara.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET", "nivara-super-secret-key-caregiver-community-2026"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))

    # Real-Time & WebSockets / Socket.IO
    SOCKETIO_PATH: str = os.getenv("SOCKETIO_PATH", "/socket.io")
    SOCKET_CORS_ALLOWED_ORIGINS: str = os.getenv("SOCKET_CORS_ALLOWED_ORIGINS", "*")
    WS_URL: str = os.getenv("WS_URL", "ws://localhost:8000/api/v1/ws")

    # Server & CORS
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

settings = Settings()
