"""
TrainRadar - TfL Live Data Connector
--------------------------------------
Fetches real live train arrivals from the
Transport for London (TfL) API.
No special approval needed — just a free API key.
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from config.settings import settings
from config.logging_config import get_logger
from ingestion.producers.kafka_producer import publish

logger = get_logger(__name__)


def build_url(endpoint: str) -> str:
    """Builds a TfL API URL with optional API key."""
    if settings.tfl_api_key:
        # Check if URL already has a query string
        if "?" in endpoint:
            url = f"{settings.tfl_base_url}{endpoint}&app_key={settings.tfl_api_key}"
        else:
            url = f"{settings.tfl_base_url}{endpoint}?app_key={settings.tfl_api_key}"
    else:
        url = f"{settings.tfl_base_url}{endpoint}"
    return url


async def fetch_arrivals(
    session: aiohttp.ClientSession,
    line: str,
    stop_id: str
) -> list:
    """
    Fetches live arrivals for a specific line and stop.

    Args:
        line:    TfL line ID e.g. "elizabeth", "victoria", "central"
        stop_id: TfL stop ID e.g. "940GZZLUSTD" (Stratford)

    Returns a list of arrival records.
    """
    url = build_url(f"/Line/{line}/Arrivals?stopPointId={stop_id}")

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return data
    except aiohttp.ClientError as exc:
        logger.error("tfl.fetch_failed", error=str(exc))
        return []


async def fetch_line_status(
    session: aiohttp.ClientSession,
    line: str
) -> list:
    """
    Fetches the current status of a TfL line.
    Returns disruption info, delays, closures etc.
    """
    url = build_url(f"/Line/{line}/Status")

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            return data
    except aiohttp.ClientError as exc:
        logger.error("tfl.status_fetch_failed", error=str(exc))
        return []


def parse_arrival(raw: dict) -> dict:
    """
    Converts a raw TfL arrival into our standard format.
    TfL uses different field names to our internal format
    so we map them here.
    """
    return {
        "train_id":        raw.get("vehicleId", "UNKNOWN"),
        "trip_id":         raw.get("tripId"),
        "route_id":        raw.get("lineId"),
        "latitude":        raw.get("latitude", 0.0),
        "longitude":       raw.get("longitude", 0.0),
        "speed_kmh":       None,
        "bearing":         None,
        "occupancy":       None,
        "destination":     raw.get("destinationName"),
        "time_to_station": raw.get("timeToStation"),  # seconds
        "platform":        raw.get("platformName"),
        "current_location": raw.get("currentLocation"),
        "source":          "tfl",
        "ingested_at":     datetime.now(timezone.utc).isoformat(),
    }


def parse_line_status(raw: dict) -> dict:
    """
    Converts a raw TfL line status into our alert format.
    """
    statuses = raw.get("lineStatuses", [])
    descriptions = []
    severity = "Good Service"

    for status in statuses:
        severity = status.get("statusSeverityDescription", "Unknown")
        reason = status.get("reason", "")
        if reason:
            descriptions.append(reason)

    return {
        "alert_id":        f"TFL_{raw.get('id', 'UNKNOWN').upper()}",
        "effect":          severity,
        "cause":           "TFL_STATUS",
        "header_text":     f"{raw.get('name')} - {severity}",
        "description_text": " ".join(descriptions) if descriptions else severity,
        "route_ids":       [raw.get("id")],
        "stop_ids":        [],
        "source":          "tfl",
        "ingested_at":     datetime.now(timezone.utc).isoformat(),
    }


async def run_tfl_connector() -> None:
    """
    Main loop — fetches real TfL data every 30 seconds
    and publishes it to Kafka.
    """
    logger.info(
        "tfl_connector.starting",
        line=settings.tfl_line,
        stop=settings.tfl_stop_id,
    )

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Fetch arrivals and line status at the same time
                arrivals_raw, status_raw = await asyncio.gather(
                    fetch_arrivals(
                        session,
                        settings.tfl_line,
                        settings.tfl_stop_id
                    ),
                    fetch_line_status(session, settings.tfl_line),
                )

                # Publish each arrival to Kafka
                for raw in arrivals_raw:
                    arrival = parse_arrival(raw)
                    await publish(
                        topic=settings.kafka_topic_raw_positions,
                        message=arrival,
                        key=arrival["train_id"],
                    )

                # Publish line status as alert
                for raw in status_raw:
                    alert = parse_line_status(raw)
                    await publish(
                        topic=settings.kafka_topic_raw_gtfs,
                        message=alert,
                        key=alert["alert_id"],
                    )

                logger.info(
                    "tfl_connector.batch_complete",
                    arrivals=len(arrivals_raw),
                    statuses=len(status_raw),
                )

            except Exception as exc:
                logger.error("tfl_connector.error", error=str(exc))

            await asyncio.sleep(settings.tfl_poll_interval_seconds)