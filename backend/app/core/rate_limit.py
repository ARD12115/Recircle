"""
Rate Limiting - Per-IP and per-user limits
"""
from fastapi import Request, HTTPException, status
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


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Rate limit exceeded: {exc.detail}",
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