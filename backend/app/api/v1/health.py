"""
Health Check Endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "recircle-api", "version": "1.0.0"}


@router.get("/version")
async def version():
    return {"version": "1.0.0", "service": "recircle-api"}