"""
TrainRadar - Positions Router
-------------------------------
API endpoints for querying train positions.
"""

from fastapi import APIRouter, Query
from typing import List, Optional
from sqlalchemy import select, desc
from api.schemas.responses import TrainPositionResponse
from db.database import get_db_session
from db.models.models import TrainPosition
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/positions", response_model=List[TrainPositionResponse])
async def get_positions(
    route_id: Optional[str] = Query(None, description="Filter by route ID"),
    limit: int = Query(100, description="Max number of results", le=1000),
):
    """
    Returns the latest train positions.
    Optionally filter by route_id.

    Example:
        GET /positions
        GET /positions?route_id=ROUTE_A
        GET /positions?limit=50
    """
    async with get_db_session() as session:
        query = select(TrainPosition).order_by(desc(TrainPosition.time)).limit(limit)

        if route_id:
            query = query.where(TrainPosition.route_id == route_id)

        result = await session.execute(query)
        positions = result.scalars().all()

    logger.info("api.positions_fetched", count=len(positions))
    return positions


@router.get("/positions/{train_id}", response_model=List[TrainPositionResponse])
async def get_train_positions(
    train_id: str,
    limit: int = Query(50, description="Max number of results", le=500),
):
    """
    Returns position history for one specific train.

    Example:
        GET /positions/IC123
    """
    async with get_db_session() as session:
        query = (
            select(TrainPosition)
            .where(TrainPosition.train_id == train_id)
            .order_by(desc(TrainPosition.time))
            .limit(limit)
        )
        result = await session.execute(query)
        positions = result.scalars().all()

    return positions