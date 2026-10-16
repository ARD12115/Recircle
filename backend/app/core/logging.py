"""
Structured Logging with Request ID
"""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional

import structlog

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> str:
    """Get or generate request ID for current context."""
    rid = request_id_var.get()
    if rid is None:
        rid = str(uuid.uuid4())[:8]
        request_id_var.set(rid)
    return rid


def set_request_id(rid: str) -> None:
    """Set request ID for current context."""
    request_id_var.set(rid)


class RequestIDFilter(logging.Filter):
    """Add request_id to log records."""
    def filter(self, record):
        record.request_id = get_request_id()
        return True


def setup_logging():
    """Configure structured logging."""
    # Standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Add request ID filter to root logger
    root_logger = logging.getLogger()
    root_logger.addFilter(RequestIDFilter())
    
    # Structlog configuration
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    """Get a structlog logger."""
    return structlog.get_logger(name)


# Audit logging
def audit_log(event: str, user_id: str = None, **kwargs):
    """Log an audit event."""
    logger = get_logger("audit")
    logger.info(
        "audit_event",
        event=event,
        user_id=user_id,
        request_id=get_request_id(),
        **kwargs,
    )