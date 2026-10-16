"""
Twin Endpoints - GET /twin, GET /twin/stream (SSE)
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_guest_user, get_user_for_stream
from app.db.session import get_db
from app.schemas.twin import TwinResponse
from app.services.twin.graph import get_twin_graph, get_twin_metrics, seed_twin
from app.services.twin.events import create_event_stream

router = APIRouter()


@router.get("", response_model=TwinResponse)
async def get_twin(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_guest_user),
):
    """Get full twin graph and current metrics."""
    # Ensure seeded
    await seed_twin(db)
    
    graph = await get_twin_graph(db)
    metrics = await get_twin_metrics(db)
    
    return TwinResponse(graph=graph, metrics=metrics)


@router.get("/stream")
async def twin_stream(
    request: Request,
    user: dict = Depends(get_user_for_stream),
):
    """Server-Sent Events stream for live twin updates."""
    return StreamingResponse(
        create_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )