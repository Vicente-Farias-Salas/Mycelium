"""Enterprise Security and Authentication."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from micelio.core.config import config

api_key_header = APIKeyHeader(name="X-Mycelium-API-Key", auto_error=False)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    """Dependency to verify the presence and correctness of the API Key."""
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    if api_key_header != config.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    return api_key_header
