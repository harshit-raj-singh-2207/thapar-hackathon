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

    # External API budget (Indian rupees per calendar month)
    MONTHLY_API_BUDGET_INR: float = float(os.getenv("MONTHLY_API_BUDGET_INR", "1500"))

    # Public product pricing. Payment processing is intentionally separate.
    PREMIUM_MONTHLY_PRICE_INR: float = float(os.getenv("PREMIUM_MONTHLY_PRICE_INR", "299"))

    # Payment provider secrets are server-only. Key ID is safe to return during checkout.
    PAYMENT_PROVIDER: str = os.getenv("PAYMENT_PROVIDER", "razorpay")
    PAYMENT_KEY_ID: str = os.getenv("PAYMENT_KEY_ID", "")
    PAYMENT_KEY_SECRET: str = os.getenv("PAYMENT_KEY_SECRET", "")
    PAYMENT_WEBHOOK_SECRET: str = os.getenv("PAYMENT_WEBHOOK_SECRET", "")
    PAYMENT_REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("PAYMENT_REQUEST_TIMEOUT_SECONDS", "10"))

    # Optional external AI. Local template/rule fallbacks remain available without a key.
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "groq")
    AI_MODEL: str = os.getenv("AI_MODEL", "llama-3.1-8b-instant")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "8"))
    AI_MAX_OUTPUT_TOKENS: int = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "180"))
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", "10"))
    AI_DUPLICATE_WINDOW_SECONDS: int = int(os.getenv("AI_DUPLICATE_WINDOW_SECONDS", "10"))
    AI_CACHE_TTL_SECONDS: int = int(os.getenv("AI_CACHE_TTL_SECONDS", "300"))
    AI_ESTIMATED_COST_INR_PER_REQUEST: float = float(os.getenv("AI_ESTIMATED_COST_INR_PER_REQUEST", "0.05"))

settings = Settings()
