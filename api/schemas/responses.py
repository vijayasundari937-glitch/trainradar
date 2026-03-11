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

class RouteStats(BaseModel):
    """Statistics for one route."""
    route_id:        str
    total_updates:   int
    avg_delay_secs:  Optional[float] = None
    max_delay_secs:  Optional[int] = None
    on_time_percent: Optional[float] = None


class SourceStats(BaseModel):
    """Breakdown of data by source."""
    source:          str
    position_count:  int


class NetworkStats(BaseModel):
    """Overall network statistics."""
    total_trains:       int
    total_positions:    int
    total_delays:       int
    total_alerts:       int
    active_alerts:      int
    avg_delay_secs:     Optional[float] = None
    max_delay_secs:     Optional[int] = None
    on_time_percent:    Optional[float] = None
    most_delayed_routes: List[RouteStats] = []
    by_source:          List[SourceStats] = []
    generated_at:       datetime