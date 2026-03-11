"""
TrainRadar - Statistics Router
--------------------------------
Returns a summary of everything happening
on the network right now.
"""

from fastapi import APIRouter
from sqlalchemy import select, func, desc
from datetime import datetime, timezone
from api.schemas.responses import NetworkStats, RouteStats, SourceStats
from db.database import get_db_session
from db.models.models import TrainPosition, TripUpdate, ServiceAlert
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/stats", response_model=NetworkStats)
async def get_stats():
    """
    Returns a full summary of the network.

    Shows:
    - How many trains are being tracked
    - How many positions have been recorded
    - Average and maximum delays
    - Which routes are most delayed
    - How many active alerts there are
    - Data breakdown by source
    """
    async with get_db_session() as session:

        # ── Count total unique trains ─────────────────────
        trains_result = await session.execute(
            select(func.count(func.distinct(TrainPosition.train_id)))
        )
        total_trains = trains_result.scalar() or 0

        # ── Count total position records ──────────────────
        positions_result = await session.execute(
            select(func.count(TrainPosition.train_id))
        )
        total_positions = positions_result.scalar() or 0

        # ── Count total delay records ─────────────────────
        delays_result = await session.execute(
            select(func.count(TripUpdate.trip_id))
        )
        total_delays = delays_result.scalar() or 0

        # ── Count total alerts ────────────────────────────
        alerts_result = await session.execute(
            select(func.count(ServiceAlert.id))
        )
        total_alerts = alerts_result.scalar() or 0

        # ── Count active alerts ───────────────────────────
        now = datetime.now(timezone.utc)
        active_alerts_result = await session.execute(
            select(func.count(ServiceAlert.id))
            .where(
                (ServiceAlert.active_until >= now) |
                (ServiceAlert.active_until.is_(None))
            )
        )
        active_alerts = active_alerts_result.scalar() or 0

        # ── Overall delay statistics ──────────────────────
        delay_stats_result = await session.execute(
            select(
                func.avg(TripUpdate.arrival_delay),
                func.max(TripUpdate.arrival_delay),
            )
        )
        delay_stats = delay_stats_result.one()
        avg_delay = round(float(delay_stats[0]), 1) if delay_stats[0] else None
        max_delay = int(delay_stats[1]) if delay_stats[1] else None

        # ── On time percentage ────────────────────────────
        # A train is "on time" if delay is less than 60 seconds
        on_time_result = await session.execute(
            select(func.count(TripUpdate.trip_id))
            .where(TripUpdate.arrival_delay < 60)
        )
        on_time_count = on_time_result.scalar() or 0
        on_time_percent = None
        if total_delays > 0:
            on_time_percent = round((on_time_count / total_delays) * 100, 1)

        # ── Most delayed routes ───────────────────────────
        route_stats_result = await session.execute(
            select(
                TripUpdate.route_id,
                func.count(TripUpdate.trip_id).label("total_updates"),
                func.avg(TripUpdate.arrival_delay).label("avg_delay"),
                func.max(TripUpdate.arrival_delay).label("max_delay"),
            )
            .where(TripUpdate.route_id.isnot(None))
            .group_by(TripUpdate.route_id)
            .order_by(desc("avg_delay"))
            .limit(5)
        )
        route_rows = route_stats_result.all()

        most_delayed_routes = []
        for row in route_rows:
            route_on_time_result = await session.execute(
                select(func.count(TripUpdate.trip_id))
                .where(
                    TripUpdate.route_id == row.route_id,
                    TripUpdate.arrival_delay < 60,
                )
            )
            route_on_time = route_on_time_result.scalar() or 0
            route_on_time_pct = None
            if row.total_updates > 0:
                route_on_time_pct = round(
                    (route_on_time / row.total_updates) * 100, 1
                )

            most_delayed_routes.append(RouteStats(
                route_id=row.route_id,
                total_updates=row.total_updates,
                avg_delay_secs=round(float(row.avg_delay), 1) if row.avg_delay else None,
                max_delay_secs=int(row.max_delay) if row.max_delay else None,
                on_time_percent=route_on_time_pct,
            ))

        # ── Data by source ────────────────────────────────
        source_result = await session.execute(
            select(
                TrainPosition.source,
                func.count(TrainPosition.train_id).label("count"),
            )
            .group_by(TrainPosition.source)
            .order_by(desc("count"))
        )
        source_rows = source_result.all()
        by_source = [
            SourceStats(source=row.source, position_count=row.count)
            for row in source_rows
        ]

    stats = NetworkStats(
        total_trains=total_trains,
        total_positions=total_positions,
        total_delays=total_delays,
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        avg_delay_secs=avg_delay,
        max_delay_secs=max_delay,
        on_time_percent=on_time_percent,
        most_delayed_routes=most_delayed_routes,
        by_source=by_source,
        generated_at=datetime.now(timezone.utc),
    )

    logger.info("api.stats_generated")
    return stats