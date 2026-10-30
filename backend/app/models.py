from sqlalchemy import Column, String, Integer, Float, Index
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
