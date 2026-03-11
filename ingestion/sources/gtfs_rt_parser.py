"""
TrainRadar - GTFS-RT Parser
-----------------------------
Fetches and parses GTFS Realtime feeds.
GTFS-RT is the international standard for real-time transit data.
It uses Protocol Buffers (binary format) — not JSON.
"""

import asyncio
from datetime import datetime, timezone
import aiohttp
from google.transit import gtfs_realtime_pb2
from config.settings import settings
from config.logging_config import get_logger
from ingestion.producers.kafka_producer import publish

logger = get_logger(__name__)


async def fetch_feed(session: aiohttp.ClientSession, url: str) -> bytes:
    """
    Downloads a GTFS-RT feed as raw bytes.
    GTFS-RT is binary (Protocol Buffers) not JSON.
    """
    headers = {}
    if settings.gtfs_rt_api_key:
        headers["Authorization"] = f"Bearer {settings.gtfs_rt_api_key}"

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.read()


def parse_vehicle_positions(feed) -> list:
    """
    Extracts vehicle position data from a GTFS-RT feed.
    Returns a list of position dicts ready to publish to Kafka.
    """
    positions = []

    for entity in feed.entity:
        # Skip entities that don't have vehicle position data
        if not entity.HasField("vehicle"):
            continue

        vehicle = entity.vehicle
        position = vehicle.position
        trip = vehicle.trip

        record = {
            "train_id":   vehicle.vehicle.id or entity.id,
            "trip_id":    trip.trip_id,
            "route_id":   trip.route_id,
            "latitude":   position.latitude,
            "longitude":  position.longitude,
            "speed_kmh":  round(position.speed * 3.6, 2) if position.speed else None,
            "bearing":    position.bearing if position.bearing else None,
            "occupancy":  str(vehicle.occupancy_status) if vehicle.occupancy_status else None,
            "source":     "gtfs-rt",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        positions.append(record)

    return positions


def parse_trip_updates(feed) -> list:
    """
    Extracts trip update (delay) data from a GTFS-RT feed.
    Returns a list of update dicts ready to publish to Kafka.
    """
    updates = []

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        trip_update = entity.trip_update
        trip = trip_update.trip

        for stop_update in trip_update.stop_time_update:
            record = {
                "trip_id":        trip.trip_id,
                "route_id":       trip.route_id,
                "stop_id":        stop_update.stop_id,
                "stop_sequence":  stop_update.stop_sequence,
                "arrival_delay":  stop_update.arrival.delay if stop_update.HasField("arrival") else None,
                "departure_delay": stop_update.departure.delay if stop_update.HasField("departure") else None,
                "schedule_rel":   str(trip.schedule_relationship),
                "source":         "gtfs-rt",
                "ingested_at":    datetime.now(timezone.utc).isoformat(),
            }
            updates.append(record)

    return updates


def parse_alerts(feed) -> list:
    """
    Extracts service alert data from a GTFS-RT feed.
    Returns a list of alert dicts ready to publish to Kafka.
    """
    alerts = []

    for entity in feed.entity:
        if not entity.HasField("alert"):
            continue

        alert = entity.alert

        # Get the English translation of the alert text
        header = ""
        description = ""
        for translation in alert.header_text.translation:
            if translation.language == "en" or not header:
                header = translation.text
        for translation in alert.description_text.translation:
            if translation.language == "en" or not description:
                description = translation.text

        # Collect affected routes and stops
        route_ids = []
        stop_ids = []
        for informed in alert.informed_entity:
            if informed.route_id:
                route_ids.append(informed.route_id)
            if informed.stop_id:
                stop_ids.append(informed.stop_id)

        record = {
            "alert_id":        entity.id,
            "effect":          str(alert.effect),
            "cause":           str(alert.cause),
            "header_text":     header,
            "description_text": description,
            "route_ids":       route_ids,
            "stop_ids":        stop_ids,
            "source":          "gtfs-rt",
            "ingested_at":     datetime.now(timezone.utc).isoformat(),
        }
        alerts.append(record)

    return alerts


async def process_vehicle_positions(session: aiohttp.ClientSession) -> int:
    """Fetch, parse and publish vehicle positions."""
    raw = await fetch_feed(session, settings.gtfs_rt_vehicle_positions_url)

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw)

    positions = parse_vehicle_positions(feed)

    for position in positions:
        await publish(
            topic=settings.kafka_topic_raw_positions,
            message=position,
            key=position["train_id"],
        )

    logger.info("gtfs_rt.positions_published", count=len(positions))
    return len(positions)


async def process_trip_updates(session: aiohttp.ClientSession) -> int:
    """Fetch, parse and publish trip updates."""
    raw = await fetch_feed(session, settings.gtfs_rt_trip_updates_url)

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw)

    updates = parse_trip_updates(feed)

    for update in updates:
        await publish(
            topic=settings.kafka_topic_raw_gtfs,
            message=update,
            key=update["trip_id"],
        )

    logger.info("gtfs_rt.updates_published", count=len(updates))
    return len(updates)


async def process_alerts(session: aiohttp.ClientSession) -> int:
    """Fetch, parse and publish service alerts."""
    raw = await fetch_feed(session, settings.gtfs_rt_alerts_url)

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw)

    alerts = parse_alerts(feed)

    for alert in alerts:
        await publish(
            topic=settings.kafka_topic_raw_gtfs,
            message=alert,
            key=alert["alert_id"],
        )

    logger.info("gtfs_rt.alerts_published", count=len(alerts))
    return len(alerts)


async def run_gtfs_rt_poller() -> None:
    """
    Main loop — fetches all 3 GTFS-RT feeds every 15 seconds.
    """
    logger.info("gtfs_rt.poller_started",
                interval=settings.gtfs_rt_poll_interval_seconds)

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Fetch all 3 feeds at the same time
                await asyncio.gather(
                    process_vehicle_positions(session),
                    process_trip_updates(session),
                    process_alerts(session),
                )
            except Exception as exc:
                logger.error("gtfs_rt.poll_error", error=str(exc))

            await asyncio.sleep(settings.gtfs_rt_poll_interval_seconds)