"""
Rate Limiting - Per-IP and per-user limits
"""
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

def get_client_ip(request: Request) -> str:
    """Get client IP, taking into account X-Forwarded-For and X-Real-IP headers."""
    if forwarded := request.headers.get("X-Forwarded-For"):
        # X-Forwarded-For can be a comma-separated list of IPs
        # The first IP is the client IP
        return forwarded.split(",")[0].strip()
    if real_ip := request.headers.get("X-Real-IP"):
        return real_ip.strip()
    # Fallback to remote address
    return request.client.host if request.client else "127.0.0.1"

# Limiter instance
limiter = Limiter(
    key_func=get_remote_address,
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
    key_func=get_remote_address,
    default_limits=["10/minute"],
    storage_uri="memory://",
)

auth_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"],
    storage_uri="memory://",
)

simulate_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20/minute"],
    storage_uri="memory://",
)

advice_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"],
    storage_uri="memory://",
)