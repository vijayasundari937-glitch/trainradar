import json
from aiokafka import AIOKafkaProducer
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
        )
        await _producer.start()
        logger.info("kafka.producer_started")
    return _producer


async def publish(topic: str, message: dict, key: str = None) -> None:
    """
    Sends a message to a Kafka topic.

    Example:
        await publish(
            topic="raw.train.positions",
            message={"train_id": "IC123", "lat": 51.5},
            key="IC123"
        )
    """
    producer = await get_producer()
    try:
        await producer.send_and_wait(topic, value=message, key=key)
        logger.info("kafka.message_published", topic=topic, key=key)
    except Exception as exc:
        logger.error("kafka.publish_failed", topic=topic, error=str(exc))
        raise


async def close_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        logger.info("kafka.producer_stopped")
        _producer = None