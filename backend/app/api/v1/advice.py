"""
Advice Endpoints - POST /advice, POST /chat
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_resident_user
from app.core.rate_limit import advice_limiter
from app.db.session import get_db
from app.schemas.advice import AdviceResponse, ChatRequest, ChatResponse, ChatMessage
from app.services.advisor.advisor import generate_advice
from app.services.advisor.llm_client import llm_client
from app.services.advisor.prompts import SYSTEM_PROMPT

router = APIRouter()


@router.post("", response_model=AdviceResponse)
@advice_limiter.limit("10/minute")
async def get_advice(
    use_cached: bool = False,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_resident_user),
):
    """Generate structured AI advice from twin metrics."""
    user_id = int(user["sub"]) if not user.get("demo") else None
    return await generate_advice(db, user_id, use_cached)


@router.post("/chat", response_model=ChatResponse)
async def chat_advisor(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_resident_user),
):
    """Streaming chat with advisor (simplified - returns full response)."""
    # Build context from twin
    from app.services.twin.metrics import compute_current_metrics
    metrics = await compute_current_metrics(db)
    
    context = f"""Current campus waste metrics:
- Diversion rate: {metrics.diversion_rate:.1%}
- Contamination rate: {metrics.contamination_rate:.1%}
- CO2e avoided: {metrics.co2e_avoided_kg:.1f} kg
- Pickup cost: ${metrics.pickup_cost:.0f}

You are a helpful waste advisor. Answer questions about recycling, reuse, repair, upcycling, and circular economy. Be concise and practical."""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
    ] + [{"role": m.role, "content": m.content} for m in request.messages]
    
    response_text = await llm_client.chat_completion(messages, temperature=0.3, max_tokens=500, use_cache=False)
    
    if not response_text:
        response_text = "I'm having trouble connecting to the advisor. Please try again later or check the structured advice."
    
    return ChatResponse(message=ChatMessage(role="assistant", content=response_text))