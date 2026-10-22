import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from backend.auth import AuthUser, get_current_user
from backend.database import get_supabase, is_supabase_configured
from backend.models import UserProfile
from backend.config import settings

logger = logging.getLogger("billbuddy.user")
router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/me", response_model=UserProfile)
async def get_user_profile(user: AuthUser = Depends(get_current_user)):
    """Get the current authenticated user's profile from Firebase Google Auth."""
    # Optionally sync with Supabase users table
    sb = get_supabase()
    if sb and is_supabase_configured():
        try:
            sb.table("users").upsert({
                "id": user.uid,
                "email": user.email,
                "name": user.name,
                "avatar_url": user.picture,
                "last_sign_in": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.debug(f"User sync note (users table might be optional): {e}")

    return UserProfile(
        uid=user.uid,
        email=user.email,
        name=user.name,
        picture=user.picture
    )


@router.get("/status")
async def get_system_status():
    """Returns the operational status of Supabase DB, Supabase Storage, and Firebase."""
    sb_configured = is_supabase_configured()
    sb_connected = False
    storage_ok = False

    if sb_configured:
        sb = get_supabase()
        if sb:
            try:
                # Test query
                sb.table("products").select("id").limit(1).execute()
                sb_connected = True
            except Exception:
                sb_connected = False

            try:
                # Test storage bucket listing
                buckets = sb.storage.list_buckets()
                bucket_names = [b.name for b in buckets] if buckets else []
                storage_ok = settings.SUPABASE_STORAGE_BUCKET in bucket_names
            except Exception:
                storage_ok = False

    return {
        "status": "online",
        "service": "BillBuddy FastAPI Backend",
        "supabase": {
            "configured": sb_configured,
            "database_connected": sb_connected,
            "storage_bucket": settings.SUPABASE_STORAGE_BUCKET,
            "storage_ready": storage_ok
        },
        "firebase": {
            "project_id": settings.FIREBASE_PROJECT_ID or "configured via client token",
            "google_auth_enabled": True
        }
    }
