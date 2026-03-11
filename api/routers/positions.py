"""
TrainRadar - Positions Router
With enhanced filtering and search.
"""

from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from api.schemas.responses import TrainPositionResponse
from db.database import get_db_session
from db.models.models import TrainPosition
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/positions", response_model=List[TrainPositionResponse])
async def get_positions(
    train_id:   Optional[str] = Query(None, description="Filter by train ID"),
    route_id:   Optional[str] = Query(None, description="Filter by route ID"),
    source:     Optional[str] = Query(None, description="Filter by source e.g. gtfs-rt, websocket"),
    since:      Optional[datetime] = Query(None, description="Only show positions after this time"),
    limit:      int = Query(100, description="Max results", le=1000),
):
    """
    Returns train positions with optional filters.

    Examples:
        GET /positions
        GET /positions?train_id=IC123
        GET /positions?route_id=ROUTE_A
        GET /positions?source=gtfs-rt
        GET /positions?since=2026-03-11T10:00:00
        GET /positions?route_id=ROUTE_A&limit=50
    """
    async with get_db_session() as session:
        query = (
            select(TrainPosition)
            .order_by(desc(TrainPosition.time))
            .limit(limit)
        )

        if train_id:
            query = query.where(TrainPosition.train_id == train_id)
        if route_id:
            query = query.where(TrainPosition.route_id == route_id)
        if source:
            query = query.where(TrainPosition.source == source)
        if since:
            query = query.where(TrainPosition.time >= since)

        result = await session.execute(query)
        positions = result.scalars().all()

    logger.info("api.positions_fetched", count=len(positions))
    return positions


@router.get("/positions/{train_id}", response_model=List[TrainPositionResponse])
async def get_train_positions(
    train_id: str,
    limit: int = Query(50, description="Max results", le=500),
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