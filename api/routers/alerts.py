"""
TrainRadar - Alerts Router
----------------------------
API endpoints for querying service alerts.
Alerts include delays, cancellations, detours etc.
"""

from fastapi import APIRouter, Query
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
    active_only: bool = Query(True, description="Only return currently active alerts"),
    route_id: Optional[str] = Query(None, description="Filter by route ID"),
    limit: int = Query(50, description="Max number of results", le=500),
):
    """
    Returns service alerts.

    Examples:
        GET /alerts
        GET /alerts?active_only=false
        GET /alerts?route_id=ROUTE_A
    """
    async with get_db_session() as session:
        query = (
            select(ServiceAlert)
            .order_by(desc(ServiceAlert.created_at))
            .limit(limit)
        )

        if active_only:
            now = datetime.now(timezone.utc)
            # Return alerts where:
            # - active_until is in the future OR active_until is not set
            query = query.where(
                or_(
                    ServiceAlert.active_until >= now,
                    ServiceAlert.active_until.is_(None),
                )
            )

        result = await session.execute(query)
        alerts = result.scalars().all()

    logger.info("api.alerts_fetched", count=len(alerts))
    return alerts


@router.get("/alerts/{alert_id}", response_model=ServiceAlertResponse)
async def get_alert(alert_id: str):
    """
    Returns one specific alert by its ID.

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
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert