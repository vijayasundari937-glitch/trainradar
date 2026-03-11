from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class TrainPositionSchema(BaseModel):
    """Validates a train position record."""
    train_id:    str
    trip_id:     Optional[str] = None
    route_id:    Optional[str] = None
    latitude:    float
    longitude:   float
    speed_kmh:   Optional[float] = None
    bearing:     Optional[float] = None
    occupancy:   Optional[str] = None
    source:      str = "unknown"
    ingested_at: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError(f"Invalid latitude: {v}")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError(f"Invalid longitude: {v}")
        return v


class TripUpdateSchema(BaseModel):
    """Validates a trip update (delay) record."""
    trip_id:         str
    route_id:        Optional[str] = None
    stop_id:         Optional[str] = None
    stop_sequence:   Optional[int] = None
    arrival_delay:   Optional[int] = None
    departure_delay: Optional[int] = None
    schedule_rel:    Optional[str] = None
    source:          str = "gtfs-rt"
    ingested_at:     Optional[str] = None


class ServiceAlertSchema(BaseModel):
    """Validates a service alert record."""
    alert_id:         str
    effect:           Optional[str] = None
    cause:            Optional[str] = None
    header_text:      Optional[str] = None
    description_text: Optional[str] = None
    route_ids:        Optional[list] = None
    stop_ids:         Optional[list] = None
    source:           str = "gtfs-rt"
    ingested_at:      Optional[str] = None