"""
TrainRadar - Search Router
Searches across positions, delays and alerts in one call.
"""

from fastapi import APIRouter, Query
from sqlalchemy import select, desc, or_
from db.database import get_db_session
from db.models.models import TrainPosition, TripUpdate, ServiceAlert
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/search")
async def search(
    q: str = Query(..., description="Search term e.g. train ID, route ID, stop ID"),
    limit: int = Query(10, description="Max results per category", le=50),
):
    """
    Searches across positions, delays and alerts at once.

    Examples:
        GET /search?q=IC123
        GET /search?q=ROUTE_A
        GET /search?q=STOP_01
        GET /search?q=DELAY
    """
    results = {
        "query":     q,
        "positions": [],
        "delays":    [],
        "alerts":    [],
    }

    async with get_db_session() as session:

        # Search positions by train_id or route_id
        pos_query = (
            select(TrainPosition)
            .where(
                or_(
                    TrainPosition.train_id.ilike(f"%{q}%"),
                    TrainPosition.route_id.ilike(f"%{q}%"),
                )
            )
            .order_by(desc(TrainPosition.time))
            .limit(limit)
        )
        pos_result = await session.execute(pos_query)
        positions = pos_result.scalars().all()
        results["positions"] = [
            {
                "train_id":  p.train_id,
                "route_id":  p.route_id,
                "latitude":  p.latitude,
                "longitude": p.longitude,
                "time":      p.time.isoformat(),
            }
            for p in positions
        ]

        # Search delays by trip_id, route_id or stop_id
        delay_query = (
            select(TripUpdate)
            .where(
                or_(
                    TripUpdate.trip_id.ilike(f"%{q}%"),
                    TripUpdate.route_id.ilike(f"%{q}%"),
                    TripUpdate.stop_id.ilike(f"%{q}%"),
                )
            )
            .order_by(desc(TripUpdate.time))
            .limit(limit)
        )
        delay_result = await session.execute(delay_query)
        delays = delay_result.scalars().all()
        results["delays"] = [
            {
                "trip_id":       d.trip_id,
                "route_id":      d.route_id,
                "stop_id":       d.stop_id,
                "arrival_delay": d.arrival_delay,
                "time":          d.time.isoformat(),
            }
            for d in delays
        ]

        # Search alerts by alert_id, effect or header_text
        alert_query = (
            select(ServiceAlert)
            .where(
                or_(
                    ServiceAlert.alert_id.ilike(f"%{q}%"),
                    ServiceAlert.effect.ilike(f"%{q}%"),
                    ServiceAlert.header_text.ilike(f"%{q}%"),
                )
            )
            .order_by(desc(ServiceAlert.created_at))
            .limit(limit)
        )
        alert_result = await session.execute(alert_query)
        alerts = alert_result.scalars().all()
        results["alerts"] = [
            {
                "alert_id":    a.alert_id,
                "effect":      a.effect,
                "header_text": a.header_text,
            }
            for a in alerts
        ]

    total = (
        len(results["positions"]) +
        len(results["delays"]) +
        len(results["alerts"])
    )
    logger.info("api.search", query=q, total=total)
    results["total_results"] = total
    return results