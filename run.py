import sys
from pathlib import Path
import uvicorn

# Reconfigure stdout/stderr to utf-8 for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to sys.path so 'backend' package imports work cleanly
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    print("=" * 60)
    print(" 🚀 Starting BillBuddy FastAPI Backend Server...")
    print(" 🌐 Application URL : http://localhost:8000")
    print(" 📖 Interactive Docs : http://localhost:8000/docs")
    print(" ⚡ Supabase DB & Storage + Firebase Google Auth")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
