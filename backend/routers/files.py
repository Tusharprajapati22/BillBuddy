import os
import re
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from backend.auth import AuthUser, get_current_user
from backend.database import get_supabase, is_supabase_configured
from backend.config import settings
from backend.models import FileUploadResponse

logger = logging.getLogger("billbuddy.files")
router = APIRouter(prefix="/files", tags=["File Storage"])

# Local uploads directory for fallback storage
LOCAL_UPLOADS_DIR = Path("uploads")
LOCAL_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and remove unsafe chars."""
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    return clean[:100]


@router.post("/upload", response_model=FileUploadResponse)
async def upload_bill_file(
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user)
):
    """
    Upload a product bill or receipt (PDF, JPG, PNG, WEBP) to Supabase Storage.
    Falls back to local upload folder if Supabase credentials are not yet configured.
    """
    ext = Path(file.filename or "receipt.png").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10 MB limit."
        )

    clean_name = sanitize_filename(file.filename or f"invoice{ext}")
    unique_filename = f"{uuid.uuid4().hex[:8]}_{clean_name}"
    storage_path = f"{user.uid}/{unique_filename}"
    bucket = settings.SUPABASE_STORAGE_BUCKET

    sb = get_supabase()
    public_url = ""

    if sb and is_supabase_configured():
        try:
            # Upload file bytes to Supabase Storage Bucket
            sb.storage.from_(bucket).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": file.content_type or "application/octet-stream"}
            )
            public_url = sb.storage.from_(bucket).get_public_url(storage_path)
            logger.info(f" File uploaded to Supabase Storage: {public_url}")
        except Exception as e:
            logger.error(f"Supabase Storage upload error: {e}. Falling back to local storage.")
            public_url = ""

    # If Supabase was not used or failed (e.g. bucket doesn't exist yet), use local fallback
    if not public_url:
        local_user_dir = LOCAL_UPLOADS_DIR / user.uid
        local_user_dir.mkdir(parents=True, exist_ok=True)
        local_filepath = local_user_dir / unique_filename

        with open(local_filepath, "wb") as f:
            f.write(file_bytes)

        # Host-relative URL
        public_url = f"/api/files/local/{user.uid}/{unique_filename}"
        storage_path = str(local_filepath)

    return FileUploadResponse(
        filename=clean_name,
        file_path=storage_path,
        public_url=public_url,
        file_size=len(file_bytes),
        content_type=file.content_type or "application/octet-stream"
    )


@router.get("/local/{user_id}/{filename}")
async def get_local_file(user_id: str, filename: str):
    """Serves locally stored files for local development mode."""
    clean_fn = sanitize_filename(filename)
    clean_uid = sanitize_filename(user_id)
    target = LOCAL_UPLOADS_DIR / clean_uid / clean_fn

    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(target)
