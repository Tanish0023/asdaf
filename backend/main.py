"""
GridBricks WindPulse - FastAPI Entrypoint Bridge
Provides direct 'main:app' discoverability for Vercel and ASGI runners.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

__all__ = ["app"]
