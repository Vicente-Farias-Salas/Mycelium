"""Enterprise Security and Authentication."""

import jwt
import time
from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from micelio.core.config import config

api_key_header = APIKeyHeader(name="X-Mycelium-API-Key", auto_error=False)
security_bearer = HTTPBearer(auto_error=False)

def create_jwt_token(subject: str, expires_delta_seconds: int = 3600) -> str:
    """Issue a JWT for a given subject (tenant/agent)."""
    payload = {
        "sub": subject,
        "exp": time.time() + expires_delta_seconds,
        "iat": time.time()
    }
    return jwt.encode(payload, config.api_key, algorithm="HS256")

async def verify_api_key(
    api_key: str = Security(api_key_header),
    bearer: HTTPAuthorizationCredentials = Security(security_bearer)
) -> str:
    """Dependency to verify API Key or JWT."""
    if api_key and api_key == config.api_key:
        return "admin"
        
    if bearer:
        try:
            payload = jwt.decode(bearer.credentials, config.api_key, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=403, detail="Invalid token")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing API Key or valid JWT Bearer token",
    )
