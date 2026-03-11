"""
TrainRadar - Health Check Router
----------------------------------
The /health endpoint tells us if the app is running.
Load balancers and monitoring tools use this.
"""

from fastapi import APIRouter
from api.schemas.responses import HealthResponse
from config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Returns the health status of the application.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
    )