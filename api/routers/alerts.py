"""
TrainRadar - Alerts Router
With enhanced filtering.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from sqlalchemy import select, desc, or_
from datetime import datetime, timezone
from api.schemas.responses import ServiceAlertResponse
from db.database import get_db_session
from db.models.models import ServiceAlert
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/alerts", response_model=List[ServiceAlertResponse])
async def get_alerts(
    active_only: bool = Query(True, description="Only return active alerts"),
    effect:      Optional[str] = Query(None, description="Filter by effect e.g. DELAY, REDUCED_SERVICE"),
    cause:       Optional[str] = Query(None, description="Filter by cause e.g. STRIKE, TECHNICAL_PROBLEM"),
    route_id:    Optional[str] = Query(None, description="Filter by route ID"),
    limit:       int = Query(50, description="Max results", le=500),
):
    """
    Returns service alerts with optional filters.

    Examples:
        GET /alerts
        GET /alerts?active_only=false
        GET /alerts?effect=DELAY
        GET /alerts?cause=STRIKE
        GET /alerts?route_id=ROUTE_A
        GET /alerts?effect=DELAY&active_only=true
    """
    async with get_db_session() as session:
        query = (
            select(ServiceAlert)
            .order_by(desc(ServiceAlert.created_at))
            .limit(limit)
        )

        if active_only:
            now = datetime.now(timezone.utc)
            query = query.where(
                or_(
                    ServiceAlert.active_until >= now,
                    ServiceAlert.active_until.is_(None),
                )
            )
        if effect:
            query = query.where(ServiceAlert.effect == effect)
        if cause:
            query = query.where(ServiceAlert.cause == cause)

        result = await session.execute(query)
        alerts = result.scalars().all()

    logger.info("api.alerts_fetched", count=len(alerts))
    return alerts


@router.get("/alerts/{alert_id}", response_model=ServiceAlertResponse)
async def get_alert(alert_id: str):
    """
    Returns one specific alert by ID.

    Example:
        GET /alerts/ALERT_001
    """
    async with get_db_session() as session:
        query = select(ServiceAlert).where(
            ServiceAlert.alert_id == alert_id
        )
        result = await session.execute(query)
        alert = result.scalar_one_or_none()

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert