import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.routers import products, files, user

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="BillBuddy - Smart Warranty Manager API with Supabase (Database & Storage) and Firebase Google Auth",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(products.router, prefix=settings.API_PREFIX)
app.include_router(files.router, prefix=settings.API_PREFIX)
app.include_router(user.router, prefix=settings.API_PREFIX)

# Root directory and frontend paths
ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
INDEX_HTML_PATH = FRONTEND_DIR / "index.html"
if not INDEX_HTML_PATH.exists():
    INDEX_HTML_PATH = ROOT_DIR / "index.html"

# Serve frontend directory statically if available
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API responsiveness."""
    return {
        "status": "healthy",
        "app": "BillBuddy",
        "version": settings.VERSION,
        "database": "Supabase PostgreSQL",
        "storage": "Supabase Storage",
        "auth": "Firebase Google Auth"
    }


@app.get("/api/config/firebase")
async def get_firebase_config():
    """Returns Firebase web client configuration loaded from .env."""
    return {
        "apiKey": settings.FIREBASE_API_KEY,
        "authDomain": settings.FIREBASE_AUTH_DOMAIN,
        "projectId": settings.FIREBASE_PROJECT_ID,
        "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
        "messagingSenderId": settings.FIREBASE_MESSAGING_SENDER_ID,
        "appId": settings.FIREBASE_APP_ID
    }


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the BillBuddy web app directly if browsed from the backend port."""
    if INDEX_HTML_PATH.exists():
        return FileResponse(INDEX_HTML_PATH)
    return HTMLResponse("<h1>BillBuddy API is running! Access <a href='/docs'>Swagger Docs</a></h1>")
