from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "TrainRadar"
    log_level: str = "INFO"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_raw_positions: str = "raw.train.positions"
    kafka_topic_raw_schedules: str = "raw.train.schedules"
    kafka_topic_raw_gtfs: str = "raw.train.gtfs"
    kafka_topic_processed: str = "processed.train.events"
    kafka_topic_dlq: str = "dead.letter.queue"
    kafka_consumer_group: str = "trainradar-etl-group"

    database_url: str = "postgresql+asyncpg://trainradar:trainradar_secret@localhost:5432/trainradar_db"
    db_user: str = "trainradar"
    db_password: str = "trainradar_secret"
    db_name: str = "trainradar_db"

    redis_url: str = "redis://localhost:6379/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()