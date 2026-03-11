"""
TrainRadar - Database Models
-----------------------------
Each class here represents one table in the database.
SQLAlchemy maps Python objects to database rows automatically.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer,
    Text, DateTime, JSON, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


class Base(DeclarativeBase):
    """
    All models inherit from this Base class.
    SQLAlchemy uses it to track all our tables.
    """
    pass


class TrainPosition(Base):
    """
    Represents one GPS position reading from a train.
    Maps to the train_positions table.
    """
    __tablename__ = "train_positions"

    # Every position needs a time and train_id together
    # to uniquely identify it
    time       = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    train_id   = Column(String(64), primary_key=True, nullable=False)
    trip_id    = Column(String(64))
    route_id   = Column(String(64))
    latitude   = Column(Float, nullable=False)
    longitude  = Column(Float, nullable=False)
    speed_kmh  = Column(Float)
    bearing    = Column(Float)
    occupancy  = Column(String(32))
    source     = Column(String(32), nullable=False, default="unknown")
    raw_payload = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class TripUpdate(Base):
    """
    Represents a delay update for a train at a specific stop.
    Maps to the trip_updates table.
    arrival_delay is in seconds — positive means late, negative means early.
    """
    __tablename__ = "trip_updates"

    time            = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    trip_id         = Column(String(64), primary_key=True, nullable=False)
    stop_sequence   = Column(Integer, primary_key=True, nullable=False)
    route_id        = Column(String(64))
    stop_id         = Column(String(64))
    arrival_delay   = Column(Integer)    # seconds late (+ = late, - = early)
    departure_delay = Column(Integer)
    arrival_time    = Column(DateTime(timezone=True))
    departure_time  = Column(DateTime(timezone=True))
    schedule_rel    = Column(String(32)) # SCHEDULED, SKIPPED, NO_DATA
    source          = Column(String(32), nullable=False, default="gtfs-rt")
    raw_payload     = Column(JSONB)
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)


class ServiceAlert(Base):
    """
    Represents a service disruption alert.
    Maps to the service_alerts table.
    """
    __tablename__ = "service_alerts"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    alert_id         = Column(String(128), nullable=False, unique=True)
    effect           = Column(String(64))   # DELAY, DETOUR, CANCELLATION
    cause            = Column(String(64))   # ACCIDENT, WEATHER, STRIKE
    header_text      = Column(Text)
    description_text = Column(Text)
    route_ids        = Column(ARRAY(Text))
    stop_ids         = Column(ARRAY(Text))
    active_from      = Column(DateTime(timezone=True))
    active_until     = Column(DateTime(timezone=True))
    source           = Column(String(32), nullable=False, default="gtfs-rt")
    raw_payload      = Column(JSONB)
    created_at       = Column(DateTime(timezone=True), default=datetime.utcnow)


class TrainSchedule(Base):
    """
    Represents one stop in a train's timetable.
    Maps to the train_schedules table.
    """
    __tablename__ = "train_schedules"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    trip_id        = Column(String(64), nullable=False)
    route_id       = Column(String(64), nullable=False)
    service_id     = Column(String(64))
    headsign       = Column(String(256))
    stop_id        = Column(String(64), nullable=False)
    stop_sequence  = Column(Integer, nullable=False)
    arrival_time   = Column(String(8))    # stored as HH:MM:SS string
    departure_time = Column(String(8))
    source         = Column(String(32), nullable=False, default="gtfs-static")
    created_at     = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("trip_id", "stop_sequence", name="uq_trip_stop"),
    )


class IngestionLog(Base):
    """
    Tracks every ingestion run.
    Tells us how many records came in, succeeded, or failed.
    """
    __tablename__ = "ingestion_log"

    time              = Column(DateTime(timezone=True), primary_key=True, default=datetime.utcnow)
    source            = Column(String(64), primary_key=True, nullable=False)
    event_type        = Column(String(64), nullable=False)
    records_received  = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_failed    = Column(Integer, default=0)
    duration_ms       = Column(Integer)
    error_message     = Column(Text)
    extra_data        = Column(JSONB)