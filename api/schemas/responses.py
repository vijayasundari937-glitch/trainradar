"""
TrainRadar - API Response Schemas
-----------------------------------
These define what our API returns to the client.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TrainPositionResponse(BaseModel):
    """Represents one train position returned by the API."""
    train_id:  str
    route_id:  Optional[str] = None
    latitude:  float
    longitude: float
    speed_kmh: Optional[float] = None
    bearing:   Optional[float] = None
    time:      datetime
    source:    str


class TripUpdateResponse(BaseModel):
    """Represents one delay update returned by the API."""
    trip_id:        str
    route_id:       Optional[str] = None
    stop_id:        Optional[str] = None
    arrival_delay:  Optional[int] = None
    departure_delay: Optional[int] = None
    time:           datetime


class ServiceAlertResponse(BaseModel):
    """Represents one service alert returned by the API."""
    alert_id:         str
    effect:           Optional[str] = None
    header_text:      Optional[str] = None
    description_text: Optional[str] = None
    route_ids:        Optional[List[str]] = None
    active_from:      Optional[datetime] = None
    active_until:     Optional[datetime] = None


class HealthResponse(BaseModel):
    """Returned by the health check endpoint."""
    status:   str
    app_name: str
    version:  str = "1.0.0"