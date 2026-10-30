from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.database import init_db
from backend.app.services.data_store import DataStore
from backend.app.routers import dates, day_ahead, metrics, sync, export

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
def health_check():
    store = DataStore()
    status = store.get_sync_status()
    return {
        "status": "healthy",
        "service": "GridBricks WindPulse Backend",
        "database": status
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to GridBricks WindPulse API. Explore /docs for OpenAPI documentation.",
        "version": "1.0.0",
        "assessment_scope": "UK National Wind Generation Actuals & Forecasts (January 2026)"
    }
