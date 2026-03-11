"""
TrainRadar - Unit Tests for Settings
"""

from config.settings import settings


def test_app_name():
    """App name should be TrainRadar."""
    assert settings.app_name == "TrainRadar"


def test_app_env():
    """App env should be development."""
    assert settings.app_env == "development"


def test_kafka_topics_not_empty():
    """All Kafka topics should be defined."""
    assert settings.kafka_topic_raw_positions != ""
    assert settings.kafka_topic_raw_schedules != ""
    assert settings.kafka_topic_raw_gtfs != ""
    assert settings.kafka_topic_processed != ""
    assert settings.kafka_topic_dlq != ""


def test_database_url_not_empty():
    """Database URL should be defined."""
    assert settings.database_url != ""
    assert "postgresql" in settings.database_url


def test_redis_url_not_empty():
    """Redis URL should be defined."""
    assert settings.redis_url != ""
    assert "redis" in settings.redis_url