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
from api.routers import health, positions, delays, alerts, search, stats
from api.auth import verify_api_key
from fastapi import Depends

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
    swagger_ui_parameters={"persistAuthorization": True},
)

# Tell Swagger UI about our API key auth
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="TrainRadar",
        version="1.0.0",
        description="Real-Time Train Data Ingestion & ETL Platform",
        routes=app.routes,
    )
    # Add the security scheme definition
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
    }
    # Apply security to ALL paths except /health and /
    for path, methods in openapi_schema["paths"].items():
        if path in ["/health", "/"]:
            continue
        for method in methods.values():
            method["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Register routers
# Health check is public — no auth needed
app.include_router(health.router, tags=["Health"])

# All other endpoints require API key
app.include_router(
    positions.router,
    tags=["Positions"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    delays.router,
    tags=["Delays"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    alerts.router,
    tags=["Alerts"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    search.router,
    tags=["Search"],
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    stats.router,
    tags=["Statistics"],
    dependencies=[Depends(verify_api_key)]
)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }