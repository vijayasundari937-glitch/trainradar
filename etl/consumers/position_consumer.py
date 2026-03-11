import json
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError
from config.settings import settings
from config.logging_config import get_logger
from db.database import get_db_session
from db.models.models import TrainPosition
from etl.validators.schemas import TrainPositionSchema

logger = get_logger(__name__)


async def save_position(data: dict) -> None:
    """Validates and saves one position record to the database."""
    try:
        # Step 1 — Validate
        validated = TrainPositionSchema(**data)

        # Step 2 — Save to database
        async with get_db_session() as session:
            position = TrainPosition(
                time=datetime.now(timezone.utc),
                train_id=validated.train_id,
                trip_id=validated.trip_id,
                route_id=validated.route_id,
                latitude=validated.latitude,
                longitude=validated.longitude,
                speed_kmh=validated.speed_kmh,
                bearing=validated.bearing,
                occupancy=validated.occupancy,
                source=validated.source,
                raw_payload=data,
            )
            session.add(position)

        logger.info("consumer.position_saved",
                    train_id=validated.train_id)

    except ValidationError as exc:
        logger.error("consumer.validation_failed",
                     error=str(exc))
    except Exception as exc:
        logger.error("consumer.save_failed",
                     error=str(exc))
        raise


async def run_position_consumer() -> None:
    """Reads position messages from Kafka and saves them to the database."""
    logger.info("position_consumer.starting",
                topic=settings.kafka_topic_raw_positions)

    consumer = AIOKafkaConsumer(
        settings.kafka_topic_raw_positions,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    await consumer.start()
    logger.info("position_consumer.started")

    try:
        async for message in consumer:
            logger.info("position_consumer.message_received",
                        offset=message.offset)
            await save_position(message.value)
    finally:
        await consumer.stop()
        logger.info("position_consumer.stopped")