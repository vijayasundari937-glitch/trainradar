"""
TrainRadar - API Authentication
---------------------------------
Protects all API endpoints with an API key.
Every request must include the header:
    X-API-Key: your-secret-key

If the key is missing or wrong, the request
is rejected with a 403 Forbidden error.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# This tells FastAPI to look for X-API-Key in request headers
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,    # we handle the error ourselves below
)


async def verify_api_key(
    api_key: str = Security(api_key_header),
) -> str:
    """
    Checks the API key in the request header.

    Returns the key if valid.
    Raises 403 if missing or wrong.

    Usage in a router:
        @router.get("/endpoint")
        async def my_endpoint(key: str = Depends(verify_api_key)):
            ...
    """
    if not api_key:
        logger.warning("auth.missing_api_key")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API key. Add X-API-Key header to your request.",
        )

    if api_key != settings.api_secret_key:
        logger.warning("auth.invalid_api_key", key_prefix=api_key[:8])
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    logger.info("auth.key_verified")
    return api_key