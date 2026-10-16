"""
Advisor Service - Build input, call LLM, validate output
"""
import json
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select

from app.services.advisor.llm_client import llm_client
from app.services.advisor.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, build_advisor_input, load_knowledge_base, TEMPLATE_ADVICE
from app.services.advisor.guard import validate_advice_output
from app.models.advice import AdviceLog
from app.models.scan import Scan
from app.models.twin import TwinNode, TwinSnapshot
from app.schemas.advice import AdviceResponse
from app.schemas.twin import MetricsResponse
from app.services.twin.routing import normalize_bin_name


async def generate_advice(
    db: AsyncSession,
    user_id: Optional[int] = None,
    use_cached: bool = False,
) -> AdviceResponse:
    """Generate structured advice from twin metrics and user history."""
    
    # Gather input data from persisted scans, campus nodes, and simulations.
    from app.services.twin.metrics import compute_current_metrics
    
    metrics = await compute_current_metrics(db)
    scans_result = await db.execute(select(Scan).where(Scan.confirmed_bin.is_not(None)))
    scans = scans_result.scalars().all()
    nodes_result = await db.execute(select(TwinNode))
    nodes = nodes_result.scalars().all()
    snapshot_result = await db.execute(
        select(TwinSnapshot).order_by(desc(TwinSnapshot.created_at), desc(TwinSnapshot.id)).limit(1)
    )
    latest_snapshot = snapshot_result.scalar_one_or_none()
    scenario_deltas = (
        latest_snapshot.metrics_json.get("deltas", {})
        if latest_snapshot and isinstance(latest_snapshot.metrics_json, dict)
        else {}
    )
    contamination_causes, hotspots = derive_advisor_context(scans, nodes)
    
    # User stats
    scans_query = select(Scan)
    if user_id is not None:
        scans_query = scans_query.where(Scan.user_id == user_id)
    user_scans_result = await db.execute(scans_query)
    user_scans = user_scans_result.scalars().all()
    user_stats = {"total_scans": len(user_scans), "classes": {}}
    for scan in user_scans:
        predicted_class = scan.predicted_class.value if hasattr(scan.predicted_class, "value") else scan.predicted_class
        user_stats["classes"][predicted_class] = user_stats["classes"].get(predicted_class, 0) + 1
    
    # Knowledge base
    knowledge_snippets = load_knowledge_base()
    
    # Build input
    input_data = build_advisor_input(
        metrics=metrics.model_dump(mode="json"),
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
    template = build_template_advice(metrics, contamination_causes, hotspots)
    
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


def derive_advisor_context(
    scans: List[Scan],
    nodes: List[TwinNode],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Summarize observed misroutes by material and campus source."""
    node_names = {node.id: node.name for node in nodes}
    causes = {}
    source_misroutes = {}
    for scan in scans:
        confirmed_bin = normalize_bin_name(scan.confirmed_bin)
        predicted_class = scan.predicted_class.value if hasattr(scan.predicted_class, "value") else scan.predicted_class
        if not confirmed_bin or predicted_class == confirmed_bin:
            continue
        pair = (predicted_class, confirmed_bin)
        causes[pair] = causes.get(pair, 0) + 1
        if scan.source_node_id is not None:
            source_id = scan.source_node_id
            source_misroutes[source_id] = source_misroutes.get(source_id, 0) + 1

    contamination_causes = [
        {
            "pair": f"{predicted}->{confirmed}",
            "count": count,
            "description": f"{count} {predicted} item(s) were confirmed in the {confirmed} bin",
        }
        for (predicted, confirmed), count in sorted(causes.items(), key=lambda item: (-item[1], item[0]))
    ][:3]
    hotspots = [
        {
            "node": node_names.get(source_id, f"Source {source_id}"),
            "issue": f"{count} confirmed scan(s) were placed in a different bin than predicted",
            "severity": "high" if count >= 5 else "medium" if count >= 2 else "low",
        }
        for source_id, count in sorted(source_misroutes.items(), key=lambda item: (-item[1], item[0]))
    ][:5]
    return contamination_causes, hotspots


def build_template_advice(
    metrics: MetricsResponse,
    contamination_causes: List[Dict[str, Any]],
    hotspots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Create fallback recommendations without inventing system measurements."""
    issues = [
        cause["description"]
        for cause in contamination_causes
    ] + [
        f"{item['node']}: {item['issue']}"
        for item in hotspots
    ]
    if not issues:
        issues = [
            "No confirmed bin choices are available yet; continue recording actual disposal choices to identify misrouting."
        ]

    if contamination_causes:
        first_cause = contamination_causes[0]
        action_why = first_cause["description"]
        action_title = f"Review signage for {first_cause['pair'].replace('->', ' to ')} sorting"
    else:
        action_why = (
            f"{metrics.total_items} scans are recorded, with {metrics.recovered_items} items confirmed in recovery bins. "
            "Additional confirmed bin choices will reveal where sorting guidance is needed."
        )
        action_title = "Continue recording actual bin choices"

    return {
        "summary": (
            f"Current persisted scans show {metrics.diversion_rate:.0%} diversion and "
            f"{metrics.contamination_rate:.0%} contamination. "
            f"{metrics.total_items} items are tracked; {metrics.recovered_items} were confirmed in recovery bins."
        ),
        "issues": issues[:5],
        "actions": [{
            "title": action_title,
            "why": action_why,
            "expected_impact": "Impact is not quantified from the available data.",
            "effort": "low",
            "owner": "facilities",
        }],
        "reuse_ideas": TEMPLATE_ADVICE["reuse_ideas"],
        "disclaimer": TEMPLATE_ADVICE["disclaimer"],
    }


# Need to import settings
from app.core.config import settings