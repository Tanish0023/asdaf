import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in project root or backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()

def get_database_url() -> str:
    """
    Returns normalized SQLAlchemy PostgreSQL connection string.
    Ensures Neon pooled connection string works seamlessly with psycopg3.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Please provide your Neon PostgreSQL pooled connection string "
            "(e.g. postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require)."
        )
    
    # Normalize schema for SQLAlchemy + psycopg 3 driver
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        
    return url

ELEXON_BASE_URL = os.getenv("ELEXON_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1")
def _get_auto_ingest() -> bool:
    for key in ("AUTO_INGEST", "Auto_ingest", "auto_ingest"):
        val = os.getenv(key)
        if val is not None and val.strip() != "":
            return val.strip().lower() in ("true", "1", "yes")
    return True

AUTO_INGEST = _get_auto_ingest()
FIXED_DECISION_CUTOFF = "11:00"  # Fixed decision cutoff time on D-1 (11:00 UTC)
ASSESSMENT_START_DATE = "2026-01-02"  # Delivery days corresponding to decisions made in Jan 2026
ASSESSMENT_END_DATE = "2026-02-01"

