"""
TrainRadar - WebSocket Listener
---------------------------------
Connects to a live WebSocket stream and receives
real-time train position updates as they happen.
Unlike REST polling, WebSocket pushes data to us instantly.
"""

import asyncio
import json
from datetime import datetime, timezone
import websockets
from config.settings import settings
from config.logging_config import get_logger
from ingestion.producers.kafka_producer import publish

logger = get_logger(__name__)


def parse_position(raw: dict) -> dict:
    """
    Cleans and standardises a raw position message.
    Every source sends data in different formats —
    this function makes them all look the same.
    """
    return {
        "train_id":   raw.get("trainId") or raw.get("train_id", "UNKNOWN"),
        "trip_id":    raw.get("tripId")  or raw.get("trip_id"),
        "route_id":   raw.get("routeId") or raw.get("route_id"),
        "latitude":   float(raw.get("lat") or raw.get("latitude", 0)),
        "longitude":  float(raw.get("lon") or raw.get("longitude", 0)),
        "speed_kmh":  raw.get("speed"),
        "bearing":    raw.get("bearing"),
        "occupancy":  raw.get("occupancy"),
        "source":     "websocket",
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


async def handle_messages(websocket) -> None:
    """
    Receives messages from the WebSocket connection one by one
    and publishes each one to Kafka.
    """
    async for raw_message in websocket:
        try:
            # Parse the JSON string into a Python dict
            data = json.loads(raw_message)

            # Standardise the format
            position = parse_position(data)

            # Publish to Kafka
            await publish(
                topic=settings.kafka_topic_raw_positions,
                message=position,
                key=position["train_id"],
            )

            logger.info(
                "ws_listener.position_received",
                train_id=position["train_id"],
                lat=position["latitude"],
                lon=position["longitude"],
            )

        except json.JSONDecodeError:
            logger.error("ws_listener.invalid_json", raw=raw_message)
        except Exception as exc:
            logger.error("ws_listener.message_error", error=str(exc))


async def run_ws_listener() -> None:
    """
    Main loop — connects to WebSocket and keeps reconnecting
    automatically if the connection drops.
    """
    logger.info("ws_listener.starting", url=settings.train_ws_url)

    while True:
        try:
            logger.info("ws_listener.connecting", url=settings.train_ws_url)

            async with websockets.connect(settings.train_ws_url) as websocket:
                logger.info("ws_listener.connected")
                await handle_messages(websocket)

        except websockets.exceptions.ConnectionClosed:
            logger.warning("ws_listener.connection_closed")

        except Exception as exc:
            logger.error("ws_listener.connection_failed", error=str(exc))

        # Wait 5 seconds before reconnecting
        logger.info("ws_listener.reconnecting_in",
                    seconds=settings.train_ws_reconnect_delay)
        await asyncio.sleep(settings.train_ws_reconnect_delay)