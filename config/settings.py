from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.tfl"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    api_secret_key: str = "trainradar-secret-key-2026"
    tfl_api_key: str = ""
    tfl_base_url: str = "https://api.tfl.gov.uk"
    tfl_line: str = "elizabeth"
    tfl_stop_id: str = "940GZZLUSTD"
    tfl_poll_interval_seconds: int = 30

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
    train_api_poll_interval_seconds: int = 30
    train_ws_url: str = "wss://live.example.com/positions"
    train_ws_reconnect_delay: int = 5
    gtfs_rt_vehicle_positions_url: str = "https://gtfs.example.com/vehicle_positions"
    gtfs_rt_trip_updates_url: str = "https://gtfs.example.com/trip_updates"
    gtfs_rt_alerts_url: str = "https://gtfs.example.com/alerts"
    gtfs_rt_poll_interval_seconds: int = 15
    gtfs_rt_api_key: str = ""

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()