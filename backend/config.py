import os
from pathlib import Path
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv

# Load .env file from the backend folder, root, or frontend folder
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Load backend/.env first, then root and frontend if present
for env_file in [BASE_DIR / ".env", ROOT_DIR / ".env", ROOT_DIR / "frontend" / ".env"]:
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)

class Settings:
    # Project info
    PROJECT_NAME: str = "BillBuddy API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    API_BASE: str = os.getenv("API_BASE", "http://localhost:8000/api")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    # Supabase credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # anon key or service_role key
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "bills")

    # Firebase configuration (Client & Auth)
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN: str = os.getenv("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_STORAGE_BUCKET: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_MESSAGING_SENDER_ID: str = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
    FIREBASE_APP_ID: str = os.getenv("FIREBASE_APP_ID", "")
    # Optional path to Firebase service account JSON if admin verification is used
    FIREBASE_SERVICE_ACCOUNT_KEY: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "")

    # CORS origins
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "*"
    ]

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
