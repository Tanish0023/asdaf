import sqlite3
import os
from contextlib import contextmanager
import backend.app.config as config

def init_db(db_path: str = None):
    target_path = db_path or config.DB_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with get_db_connection(target_path) as conn:
        cursor = conn.cursor()
        
        # Actuals table (from FUELHH, wind only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actual_wind (
                startTime TEXT PRIMARY KEY,
                publishTime TEXT,
                settlementDate TEXT,
                settlementPeriod INTEGER,
                generation REAL NOT NULL
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actual_startTime ON actual_wind(startTime);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actual_settlementDate ON actual_wind(settlementDate);")

        # Forecasts table (from WINDFOR)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecast_wind (
                publishTime TEXT NOT NULL,
                startTime TEXT NOT NULL,
                generation REAL NOT NULL,
                PRIMARY KEY (publishTime, startTime)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_forecast_startTime ON forecast_wind(startTime);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_forecast_publishTime ON forecast_wind(publishTime);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_forecast_lookup ON forecast_wind(startTime, publishTime);")

        # Sync log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                synced_at TEXT NOT NULL,
                records_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            );
        """)
        conn.commit()

@contextmanager
def get_db_connection(db_path: str = None):
    target_path = db_path or config.DB_PATH
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
