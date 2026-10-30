import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "wind_data.db"))
ELEXON_BASE_URL = os.getenv("ELEXON_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1")

DEFAULT_CUTOFF_TIME = "11:00"  # UK wholesale day-ahead gate closure (11:00 UTC)
ASSESSMENT_START_DATE = "2026-01-01"
ASSESSMENT_END_DATE = "2026-01-31"
