"""
TrainRadar - Delays Router
----------------------------
API endpoints for querying train delay information.
arrival_delay is in seconds — positive = late, negative = early.
"""

from fastapi import APIRouter, Query
from typing import List, Optional
from sqlalchemy import select, desc
from api.schemas.responses import TripUpdateResponse
from db.database import get_db_session
from db.models.models import TripUpdate
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/delays", response_model=List[TripUpdateResponse])
async def get_delays(
    route_id: Optional[str] = Query(None, description="Filter by route ID"),
    min_delay: Optional[int] = Query(None, description="Minimum delay in seconds"),
    limit: int = Query(100, description="Max number of results", le=1000),
):
    """
    Returns the latest trip delay updates.

    Examples:
        GET /delays
        GET /delays?route_id=ROUTE_A
        GET /delays?min_delay=60   (only show trains 60+ seconds late)
    """
    async with get_db_session() as session:
        query = (
            select(TripUpdate)
            .order_by(desc(TripUpdate.time))
            .limit(limit)
        )

        if route_id:
            query = query.where(TripUpdate.route_id == route_id)

        if min_delay is not None:
            query = query.where(TripUpdate.arrival_delay >= min_delay)

        result = await session.execute(query)
        updates = result.scalars().all()

    logger.info("api.delays_fetched", count=len(updates))
    return updates


@router.get("/delays/{trip_id}", response_model=List[TripUpdateResponse])
async def get_trip_delays(
    trip_id: str,
    limit: int = Query(50, description="Max number of results", le=500),
):
    """
    Returns delay history for one specific trip.

    Example:
        GET /delays/TRIP001
    """
    async with get_db_session() as session:
        query = (
            select(TripUpdate)
            .where(TripUpdate.trip_id == trip_id)
            .order_by(desc(TripUpdate.time))
            .limit(limit)
        )
        result = await session.execute(query)
        updates = result.scalars().all()

    logger.info("api.trip_delays_fetched",
                trip_id=trip_id, count=len(updates))
    return updates