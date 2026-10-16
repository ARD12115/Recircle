"""
Advice Endpoints - POST /advice, POST /chat
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_guest_user
from app.core.rate_limit import advice_limiter
from app.db.session import get_db
from app.schemas.advice import AdviceResponse
from app.services.advisor.advisor import generate_advice, load_sample_advice

router = APIRouter()


@router.post("", response_model=AdviceResponse)
@advice_limiter.limit("10/minute")
async def get_advice(
    request: Request,
    use_cached: bool = False,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_guest_user),
):
    """Generate structured AI advice from twin metrics."""
    if user.get("role") == "guest":
        return load_sample_advice()
    user_id = int(user["sub"]) if not user.get("demo") else None
    return await generate_advice(db, user_id, use_cached)