from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from app.config import get_database_url
from app.models import Base

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_database_url()
        # Configure SQLAlchemy engine optimized for Neon PostgreSQL pooled connections
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,      # Detects dropped/stale Neon serverless connections
            pool_recycle=300,        # Recycles connections every 5 min
            pool_size=10,
            max_overflow=20,
            echo=False
        )
    return _engine

def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

def init_db():
    """
    Initializes PostgreSQL database tables and indexes on Neon.
    """
    engine = get_engine()
    logger.info("Initializing Neon PostgreSQL schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Neon PostgreSQL schema created successfully.")

@contextmanager
def get_db():
    """
    Provides a transactional scope around a series of operations.
    """
    SessionLocal = get_session_factory()
    session: Session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
