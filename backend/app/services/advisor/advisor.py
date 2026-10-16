"""
Advisor Service - Build input, call LLM, validate output
"""
import json
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.advisor.llm_client import llm_client
from app.services.advisor.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, build_advisor_input, load_knowledge_base, TEMPLATE_ADVICE
from app.services.advisor.guard import validate_advice_output
from app.models.advice import AdviceLog
from app.schemas.advice import AdviceResponse


async def generate_advice(
    db: AsyncSession,
    user_id: Optional[int] = None,
    use_cached: bool = False,
) -> AdviceResponse:
    """Generate structured advice from twin metrics and user history."""
    
    # Gather input data
    from app.services.twin.metrics import compute_current_metrics
    from app.services.twin.graph import get_twin_graph
    
    metrics = await compute_current_metrics(db)
    graph = await get_twin_graph(db)
    
    # Contamination causes (simplified)
    contamination_causes = [
        {"pair": "recyclable->residual", "count": 45, "description": "Recyclables in residual bin"},
        {"pair": "biodegradable->residual", "count": 38, "description": "Food waste in landfill"},
        {"pair": "hazardous->recyclable", "count": 3, "description": "Batteries in recycling"},
    ]
    
    # Hotspot nodes
    hotspots = [
        {"node": "Hostel A", "issue": "High contamination in recyclable bin", "severity": "high"},
        {"node": "Canteen", "issue": "Organic waste not separated", "severity": "high"},
        {"node": "Library", "issue": "Paper contamination", "severity": "medium"},
    ]
    
    # Scenario deltas (from last simulation)
    scenario_deltas = {
        "diversion_rate": 0.12,
        "contamination_rate": -0.05,
        "co2e_avoided_kg": 15.3,
        "pickup_cost": -200.0,
    }
    
    # User stats
    user_stats = {"total_scans": 0, "classes": {}}
    if user_id:
        from app.models.scan import Scan
        result = await db.execute(select(Scan).where(Scan.user_id == user_id))
        scans = result.scalars().all()
        user_stats = {
            "total_scans": len(scans),
            "classes": {},
        }
        for scan in scans:
            user_stats["classes"][scan.predicted_class] = user_stats["classes"].get(scan.predicted_class, 0) + 1
    
    # Knowledge base
    knowledge_snippets = load_knowledge_base()
    
    # Build input
    input_data = build_advisor_input(
        metrics=metrics.model_dump(),
        contamination_causes=contamination_causes,
        hotspots=hotspots,
        scenario_deltas=scenario_deltas,
        user_stats=user_stats,
        knowledge_snippets=knowledge_snippets,
    )
    
    # Check cache
    input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
    
    # Check DB cache
    result = await db.execute(select(AdviceLog).where(AdviceLog.input_hash == input_hash))
    cached = result.scalar_one_or_none()
    
    if use_cached and cached:
        return AdviceResponse(**cached.output_json, cached=True, provider=cached.provider)
    
    # Build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(input_json=json.dumps(input_data, indent=2))},
    ]
    
    # Call LLM
    response_text = await llm_client.chat_completion(messages, temperature=0.1, max_tokens=1500)
    
    if response_text:
        try:
            advice_data = json.loads(response_text)
            # Validate
            validated = validate_advice_output(advice_data, input_data)
            if validated:
                # Log to DB
                advice_log = AdviceLog(
                    user_id=user_id,
                    input_hash=input_hash,
                    output_json=validated,
                    provider=settings.LLM_PRIMARY_PROVIDER,
                )
                db.add(advice_log)
                await db.commit()
                return AdviceResponse(**validated, cached=False, provider=settings.LLM_PRIMARY_PROVIDER)
        except json.JSONDecodeError:
            pass
    
    # Fallback to template
    template = TEMPLATE_ADVICE.copy()
    template["summary"] = template["summary"].format(
        diversion_rate=metrics.diversion_rate,
        contamination_rate=metrics.contamination_rate,
        total_items=metrics.total_items,
        recovered_items=metrics.recovered_items,
    )
    
    # Log template fallback
    advice_log = AdviceLog(
        user_id=user_id,
        input_hash=input_hash,
        output_json=template,
        provider="template",
    )
    db.add(advice_log)
    await db.commit()
    
    return AdviceResponse(**template, cached=True, provider="template")


# Need to import settings
from app.core.config import settings