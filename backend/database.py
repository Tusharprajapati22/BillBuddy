import logging
from typing import Optional
from supabase import create_client, Client
from backend.config import settings

logger = logging.getLogger("billbuddy.database")

_supabase_client: Optional[Client] = None

def get_supabase() -> Optional[Client]:
    """
    Returns an initialized Supabase client instance.
    If SUPABASE_URL or SUPABASE_KEY is missing, logs a warning.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    url = settings.SUPABASE_URL.strip()
    key = settings.SUPABASE_KEY.strip()

    if not url or not key or "your-supabase" in url:
        logger.warning(
            "⚠️ Supabase URL or Key is not configured in backend/.env. "
            "Please configure SUPABASE_URL and SUPABASE_KEY to enable live database and storage sync."
        )
        return None

    try:
        _supabase_client = create_client(url, key)
        logger.info(" Connected to Supabase successfully!")
        return _supabase_client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        return None

def is_supabase_configured() -> bool:
    """Checks if valid Supabase credentials have been provided."""
    url = settings.SUPABASE_URL.strip()
    key = settings.SUPABASE_KEY.strip()
    return bool(url and key and "your-supabase" not in url)
