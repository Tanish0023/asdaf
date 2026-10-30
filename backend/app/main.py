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

from app.database import init_db
from app.services.data_store import DataStore
from app.routers import dates, day_ahead, metrics, sync, export

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("gridbricks.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    logger.info("Initializing Neon PostgreSQL database...")
    init_db()
    
    store = DataStore()
    status = store.get_sync_status()
    logger.info(f"DB initialized. Current records: {status['actual_count']} actuals, {status['forecast_count']} forecasts.")
    
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
app.include_router(sync.router)
app.include_router(export.router)

@app.get("/health")
@app.get("/api/health")
def health_check():
    store = DataStore()
    status = store.get_sync_status()
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

