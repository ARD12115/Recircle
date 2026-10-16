"""
Advisor Prompts - Build input, system prompt
"""
import json
from typing import Dict, Any, List
from pathlib import Path


SYSTEM_PROMPT = """You are ReCircle's Circular Economy Advisor. Your role is to analyze campus waste system metrics and provide grounded, actionable recommendations.

STRICT RULES:
1. NEVER invent numbers. Every figure in your output MUST appear in the input JSON.
2. If input lacks a number you need, say "data not available" - do not estimate.
3. Output MUST match the exact JSON schema provided.
4. Focus on waste, reuse, repair, upcycling, and circular economy topics only.
5. Be concise. Prioritize high-impact, low-effort actions.
6. Include a disclaimer that guidance is informational and local rules apply."""

USER_PROMPT_TEMPLATE = """Analyze this campus waste system and provide structured recommendations.

INPUT DATA:
{input_json}

OUTPUT SCHEMA (must match exactly):
{{
  "summary": "2-3 sentence executive summary of system state",
  "issues": ["issue 1", "issue 2", ...],
  "actions": [
    {{
      "title": "Action title",
      "why": "Why this matters, referencing input numbers",
      "expected_impact": "Quantified impact from input data (e.g., '+12% diversion')",
      "effort": "low|medium|high",
      "owner": "residents|facilities|management"
    }}
  ],
  "reuse_ideas": ["idea 1", "idea 2", ...],
  "disclaimer": "Guidance is informational. Local disposal rules may vary. Consult facility staff for hazardous items."
}}

CONSTRAINTS:
- Maximum 5 actions, ranked by impact/effort ratio
- Every number in expected_impact must trace to input
- reuse_ideas: practical upcycling/repair suggestions for common items
- If LLM is unavailable, a template fallback will be used"""


def build_advisor_input(
    metrics: Dict[str, Any],
    contamination_causes: List[Dict[str, Any]],
    hotspots: List[Dict[str, Any]],
    scenario_deltas: Dict[str, float],
    user_stats: Dict[str, Any],
    knowledge_snippets: List[str],
) -> Dict[str, Any]:
    """Build structured input for advisor LLM."""
    return {
        "metrics": metrics,
        "top_contamination_causes": contamination_causes[:3],
        "hotspot_nodes": hotspots[:5],
        "scenario_deltas": scenario_deltas,
        "user_scan_stats": user_stats,
        "knowledge_base": knowledge_snippets[:5],
    }


def load_knowledge_base() -> List[str]:
    """Load disposal/reuse knowledge snippets."""
    kb_path = Path(__file__).parent.parent.parent / "data" / "knowledge"
    snippets = []
    
    if kb_path.exists():
        for md_file in kb_path.glob("*.md"):
            try:
                with open(md_file) as f:
                    content = f.read()
                    # Split into paragraphs
                    for para in content.split("\n\n"):
                        para = para.strip()
                        if len(para) > 50:
                            snippets.append(para[:500])
            except Exception:
                pass
    
    # Default snippets if none loaded
    if not snippets:
        snippets = [
            "Plastic bottles (PET #1) are highly recyclable when clean and caps-on.",
            "Food-contaminated cardboard (pizza boxes) should go to compost, not recycling.",
            "Lithium-ion batteries (phones, laptops) are fire hazards in compactors - always use hazardous collection.",
            "Textiles in good condition: donate. Worn textiles: textile recycling bins.",
            "Glass jars: rinse, remove lids, separate by color if required locally.",
            "Aluminum cans: infinitely recyclable, 95% energy savings vs virgin.",
            "Electronics: never in general waste. Use e-waste collection points.",
            "Compostable plastics: only in industrial compost, not home compost or recycling.",
        ]
    
    return snippets


# Template fallback for when LLM is unavailable
TEMPLATE_ADVICE = {
    "reuse_ideas": [
        "Glass jars → storage containers, planters",
        "Cardboard boxes → organizers, compost brown material",
        "Old textiles → cleaning rags, pet bedding",
        "Plastic containers → seed starters, hardware organizers",
    ],
    "disclaimer": "Guidance is informational. Local disposal rules may vary. Consult facility staff for hazardous items.",
}