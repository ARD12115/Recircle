"""
API v1 Router - Mounts all v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1 import auth, scan, history, twin, simulate, advice, chat, reports, admin, health

api_router = APIRouter()

# Public endpoints
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Guest + authenticated endpoints
api_router.include_router(scan.router, prefix="/scan", tags=["scan"])
api_router.include_router(twin.router, prefix="/twin", tags=["twin"])
api_router.include_router(simulate.router, prefix="/simulate", tags=["simulate"])

# Authenticated endpoints
api_router.include_router(history.router, prefix="/scans", tags=["history"])
api_router.include_router(advice.router, prefix="/advice", tags=["advice"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# Admin endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])