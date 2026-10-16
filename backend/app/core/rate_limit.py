"""
Rate Limiting - Per-IP and per-user limits
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

def get_client_ip(request: Request) -> str:
    """Use the ASGI peer, which Uvicorn rewrites only for trusted proxies."""
    return request.client.host if request.client else "127.0.0.1"

# Limiter instance
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{settings.RATE_LIMIT_PER_MIN}/minute"],
    storage_uri="memory://",
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limited",
                "message": "Too many requests. Wait a minute and retry.",
            }
        },
        headers={"Retry-After": "60"},
    )


# Specific limiters
scan_limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["10/minute"],
    storage_uri="memory://",
)

auth_limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["5/minute"],
    storage_uri="memory://",
)

simulate_limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["20/minute"],
    storage_uri="memory://",
)

advice_limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["10/minute"],
    storage_uri="memory://",
)