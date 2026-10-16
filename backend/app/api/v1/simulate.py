"""
Simulate Endpoint - POST /simulate
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_guest_user
from app.core.rate_limit import simulate_limiter
from app.db.session import get_db
from app.schemas.twin import SimulateRequest, SimulateResponse
from app.services.twin.engine import TwinEngine, create_initial_state

router = APIRouter()


@router.post("", response_model=SimulateResponse)
@simulate_limiter.limit("20/minute")
async def run_simulation(
    request: SimulateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_guest_user),
):
    """Run what-if simulation with baseline vs scenario comparison."""
    engine = TwinEngine(seed=42)
    initial_state = create_initial_state()
    
    result = engine.run_simulation(initial_state, request)
    return result