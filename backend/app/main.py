import os
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path so 'app.*' imports work in all environments
CURRENT_DIR = Path(__file__).resolve().parent  # backend/app
BACKEND_DIR = CURRENT_DIR.parent               # backend
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import AUTO_INGEST
from app.database import init_db
from app.services.data_store import DataStore
from app.services.ingest_service import ensure_data_ingested
from app.routers import dates, day_ahead, metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("gridbricks.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    init_db()
    
    store = DataStore()
    status = store.get_data_status()
    logger.info(f"Database connected. Records: {status['actual_count']} actuals, {status['forecast_count']} forecasts.")

    if not status.get("is_complete"):
        if AUTO_INGEST:
            logger.info("Database records missing or incomplete. AUTO_INGEST enabled: fetching 31 Dec 2025 - 2 Feb 2026 wind datasets from Elexon BMRS...")
            try:
                await ensure_data_ingested()
                new_status = store.get_data_status()
                logger.info(f"Ingestion complete: {new_status['actual_count']} actuals, {new_status['forecast_count']} forecasts.")
            except Exception as e:
                logger.warning(f"Auto-ingest encountered error: {e}. API starting with existing records.")
        else:
            logger.warning("Database records missing or incomplete, but auto-ingestion is disabled (AUTO_INGEST=false). Serving existing database records.")
    else:
        logger.info("Database contains complete dataset (31 Dec 2025 - 2 Feb 2026). Ingestion skipped.")
    
    yield
    logger.info("Shutting down GridBricks API...")

app = FastAPI(
    title="GridBricks WindPulse API",
    description="UK Wholesale Day-Ahead Renewable Generation Forecast & Accuracy Evaluation Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Enable CORS for frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(dates.router)
app.include_router(day_ahead.router)
app.include_router(metrics.router)

@app.get("/health")
@app.get("/api/health")
def health_check():
    store = DataStore()
    status = store.get_data_status()
    return {
        "status": "healthy",
        "service": "GridBricks WindPulse Backend",
        "database": status
    }

@app.get("/")
@app.get("/api")
def root():
    return {
        "message": "Welcome to GridBricks WindPulse API. Explore /api/docs for OpenAPI documentation.",
        "version": "1.0.0",
        "assessment_scope": "UK National Wind Generation Actuals & Forecasts (January 2026)"
    }

@app.get("/docs", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/api/docs")

@app.get("/redoc", include_in_schema=False)
def redoc_redirect():
    return RedirectResponse(url="/api/redoc")

@app.get("/openapi.json", include_in_schema=False)
def openapi_redirect():
    return RedirectResponse(url="/api/openapi.json")

