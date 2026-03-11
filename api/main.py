"""
TrainRadar - Main FastAPI Application
---------------------------------------
This is the entry point of the entire application.
It starts all services and exposes the API.
"""

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from config.settings import settings
from config.logging_config import setup_logging, get_logger
from api.routers import health, positions, delays, alerts, search

# Set up logging first
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Everything before yield runs on startup.
    Everything after yield runs on shutdown.
    """
    logger.info("trainradar.starting", env=settings.app_env)

    # Start background tasks
    tasks = []

    # Import here to avoid circular imports
    from ingestion.sources.rest_poller import run_rest_poller
    from etl.consumers.position_consumer import run_position_consumer

    # Start REST poller in background
    tasks.append(asyncio.create_task(run_rest_poller()))
    logger.info("trainradar.rest_poller_started")

    # Start ETL consumer in background
    tasks.append(asyncio.create_task(run_position_consumer()))
    logger.info("trainradar.consumer_started")

    logger.info("trainradar.ready")
    yield

    # Shutdown — cancel all background tasks
    logger.info("trainradar.shutting_down")
    for task in tasks:
        task.cancel()

    # Close connections
    from ingestion.producers.kafka_producer import close_producer
    from db.database import close_engine
    await close_producer()
    await close_engine()
    logger.info("trainradar.stopped")


# Create the FastAPI app
app = FastAPI(
    title="TrainRadar",
    description="Real-Time Train Data Ingestion & ETL Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(health.router, tags=["Health"])
app.include_router(positions.router, tags=["Positions"])
app.include_router(delays.router, tags=["Delays"])
app.include_router(alerts.router, tags=["Alerts"])
app.include_router(search.router, tags=["Search"])


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }