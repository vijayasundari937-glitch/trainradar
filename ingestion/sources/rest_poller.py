"""
TrainRadar - REST API Poller
-----------------------------
Fetches train schedule data from a REST API every 30 seconds
and publishes it to Kafka.
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from config.settings import settings
from config.logging_config import get_logger
from ingestion.producers.kafka_producer import publish

logger = get_logger(__name__)


async def fetch_schedules(session: aiohttp.ClientSession) -> list:
    """
    Makes one HTTP GET request to the train schedules API.
    Returns a list of schedule records.

    In a real project this would call a real API like:
    - National Rail (UK)
    - Amtrak (USA)
    - Deutsche Bahn (Germany)
    For now we simulate the response so you can see it working.
    """
    try:
        # ── Simulated API response ─────────────────────────
        # Replace this with a real API call like:
        # async with session.get(
        #     f"{settings.train_api_base_url}/schedules",
        #     headers={"Authorization": f"Bearer {settings.train_api_key}"}
        # ) as response:
        #     data = await response.json()
        #     return data["schedules"]

        # Simulated data — 3 trains with schedules
        simulated_data = [
            {
                "trip_id": "TRIP001",
                "route_id": "ROUTE_A",
                "headsign": "London Waterloo",
                "stop_id": "STOP_01",
                "stop_sequence": 1,
                "arrival_time": "08:00:00",
                "departure_time": "08:02:00",
                "service_id": "SVC_MON_FRI",
            },
            {
                "trip_id": "TRIP001",
                "route_id": "ROUTE_A",
                "headsign": "London Waterloo",
                "stop_id": "STOP_02",
                "stop_sequence": 2,
                "arrival_time": "08:15:00",
                "departure_time": "08:17:00",
                "service_id": "SVC_MON_FRI",
            },
            {
                "trip_id": "TRIP002",
                "route_id": "ROUTE_B",
                "headsign": "Manchester Piccadilly",
                "stop_id": "STOP_03",
                "stop_sequence": 1,
                "arrival_time": "09:00:00",
                "departure_time": "09:05:00",
                "service_id": "SVC_MON_FRI",
            },
        ]
        return simulated_data

    except aiohttp.ClientError as exc:
        logger.error("rest_poller.fetch_failed", error=str(exc))
        return []


async def run_rest_poller() -> None:
    """
    Main loop — runs forever, fetching schedules every 30 seconds.
    Each record gets published to the raw.train.schedules Kafka topic.
    """
    logger.info("rest_poller.started",
                interval=settings.train_api_poll_interval_seconds)

    # Create one HTTP session and reuse it
    async with aiohttp.ClientSession() as session:
        while True:
            start_time = datetime.now(timezone.utc)
            records_fetched = 0

            try:
                schedules = await fetch_schedules(session)

                for schedule in schedules:
                    # Add metadata before publishing
                    schedule["ingested_at"] = start_time.isoformat()
                    schedule["source"] = "rest_api"

                    # Publish to Kafka
                    await publish(
                        topic=settings.kafka_topic_raw_schedules,
                        message=schedule,
                        key=schedule.get("trip_id"),
                    )
                    records_fetched += 1

                logger.info(
                    "rest_poller.batch_complete",
                    records=records_fetched,
                )

            except Exception as exc:
                logger.error("rest_poller.error", error=str(exc))

            # Wait 30 seconds before next poll
            await asyncio.sleep(settings.train_api_poll_interval_seconds)