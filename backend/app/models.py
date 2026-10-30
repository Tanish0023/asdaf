from sqlalchemy import Column, String, Integer, Float, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ActualWind(Base):
    __tablename__ = "actual_wind"

    start_time = Column(String(30), primary_key=True, index=True)
    publish_time = Column(String(30), nullable=False)
    settlement_date = Column(String(10), nullable=False, index=True)
    settlement_period = Column(Integer, nullable=False)
    generation = Column(Float, nullable=False)

    __table_args__ = (
        Index("idx_actual_date_period", "settlement_date", "settlement_period"),
        Index("idx_actual_start_time", "start_time"),
    )

class ForecastWind(Base):
    __tablename__ = "forecast_wind"

    publish_time = Column(String(30), primary_key=True)
    start_time = Column(String(30), primary_key=True, index=True)
    generation = Column(Float, nullable=False)

    __table_args__ = (
        Index("idx_forecast_lookup", "start_time", "publish_time"),
        Index("idx_forecast_publish_time", "publish_time"),
    )

class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset = Column(String(50), nullable=False)
    synced_at = Column(String(30), nullable=False)
    records_count = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)
