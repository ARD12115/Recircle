#!/usr/bin/env python3
"""
ReCircle Logging Utility
Usage:
    from scripts.log_util import log, log_error, log_info, log_debug
    log_info("backend", "Server started on port 8000")
    log_error("ml", "Failed to load model", exc_info=True)
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Format
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(component)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure root logger to also write to errors.log
class ComponentFilter(logging.Filter):
    def filter(self, record):
        record.component = getattr(record, 'component', 'app')
        return True

def _get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"recircle.{name}")
    logger.setLevel(logging.DEBUG)
    logger.addFilter(ComponentFilter())
    
    # File handler - all logs
    fh = logging.FileHandler(LOG_DIR / "build.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(fh)
    
    # Error handler - errors only to errors.log
    eh = logging.FileHandler(LOG_DIR / "errors.log", encoding="utf-8")
    eh.setLevel(logging.ERROR)
    eh.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(eh)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(ch)
    
    logger.propagate = False
    return logger

# Pre-configured loggers per component
_loggers = {}
def _logger(component: str) -> logging.Logger:
    if component not in _loggers:
        _loggers[component] = _get_logger(component)
    return _loggers[component]

def log_debug(component: str, message: str, **kwargs):
    _logger(component).debug(message, extra=kwargs)

def log_info(component: str, message: str, **kwargs):
    _logger(component).info(message, extra=kwargs)

def log_warn(component: str, message: str, **kwargs):
    _logger(component).warning(message, extra=kwargs)

def log_error(component: str, message: str, exc_info: bool = False, **kwargs):
    _logger(component).error(message, exc_info=exc_info, extra=kwargs)

def log_exception(component: str, message: str, **kwargs):
    _logger(component).exception(message, extra=kwargs)

# Convenience aliases
debug = log_debug
info = log_info
warn = log_warn
error = log_error
exception = log_exception

if __name__ == "__main__":
    # Test
    info("test", "Build log system initialized")
    debug("backend", "Debug message")
    warn("ml", "Low GPU memory")
    try:
        raise ValueError("Test error")
    except Exception:
        error("api", "Request failed", exc_info=True)
    print(f"\nLogs written to {LOG_DIR}")