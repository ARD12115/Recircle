"""Advisor chat endpoint."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import advice_limiter
from app.core.security import get_resident_user
from app.db.session import get_db
from app.schemas.advice import ChatMessage, ChatRequest, ChatResponse
from app.services.advisor.llm_client import llm_client
from app.services.advisor.prompts import SYSTEM_PROMPT
from app.services.twin.metrics import compute_current_metrics

router = APIRouter()


@router.post("", response_model=ChatResponse)
@advice_limiter.limit("10/minute")
async def chat_advisor(
    request: Request,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_resident_user),
):
    """Answer recycling questions using current campus metrics as context."""
    metrics = await compute_current_metrics(db)
    context = f"""Current campus waste metrics:
- Diversion rate: {metrics.diversion_rate:.1%}
- Contamination rate: {metrics.contamination_rate:.1%}
- CO2e avoided: {metrics.co2e_avoided_kg:.1f} kg
- Pickup cost: ${metrics.pickup_cost:.0f}

You are a helpful waste advisor. Answer questions about recycling, reuse, repair, upcycling, and circular economy. Be concise and practical."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
        *[
            {"role": message.role, "content": message.content}
            for message in chat_request.messages
        ],
    ]
    response_text = await llm_client.chat_completion(
        messages,
        temperature=0.3,
        max_tokens=500,
        use_cache=False,
    )

    if not response_text:
        response_text = (
            "I'm having trouble connecting to the advisor. Please try again later "
            "or check the structured advice."
        )

    return ChatResponse(message=ChatMessage(role="assistant", content=response_text))
