"""
Vision Guidance - Class to bin and preparation steps
"""
import json
from pathlib import Path
from typing import Dict, Any


# Load bin rules from data file
_rules_cache = None


def load_rules() -> Dict[str, Any]:
    global _rules_cache
    if _rules_cache is None:
        rules_path = Path(__file__).parent.parent.parent / "data" / "bin_rules.json"
        if rules_path.exists():
            with open(rules_path) as f:
                _rules_cache = json.load(f)
        else:
            _rules_cache = get_default_rules()
    return _rules_cache


def get_default_rules() -> Dict[str, Any]:
    """Default disposal guidance rules."""
    return {
        "recyclable": {
            "paper": {"bin": "Blue bin (Paper/Cardboard)", "steps": ["Flatten boxes", "Remove plastic wrap", "Keep dry"], "why": "Paper fibers recover well when clean and dry"},
            "cardboard": {"bin": "Blue bin (Paper/Cardboard)", "steps": ["Flatten", "Remove tape", "No greasy pizza boxes"], "why": "Clean cardboard recycles to new boxes"},
            "plastic": {"bin": "Yellow bin (Plastic/Metal)", "steps": ["Rinse containers", "Leave caps on", "Check resin code 1,2,5"], "why": "Clean plastics avoid contamination"},
            "metal": {"bin": "Yellow bin (Plastic/Metal)", "steps": ["Rinse cans", "No aerosol cans", "Aluminum foil clean"], "why": "Metals infinitely recyclable"},
            "glass": {"bin": "Green bin (Glass)", "steps": ["Rinse jars", "No lids", "No ceramics/Pyrex"], "why": "Glass recycles endlessly when separated"},
        },
        "reusable": {
            "textile": {"bin": "Donation bin / Textile collection", "steps": ["Wash if possible", "Bag separately", "Check local charity"], "why": "Clothes/shoes reuse beats recycling"},
            "footwear": {"bin": "Donation bin / Shoe collection", "steps": ["Pair shoes", "Tie laces", "Good condition preferred"], "why": "Footwear reuse extends life"},
        },
        "biodegradable": {
            "organic": {"bin": "Green bin (Compost/Food waste)", "steps": ["No plastic bags", "Remove packaging", "Drain liquids"], "why": "Organic waste becomes compost/biogas"},
        },
        "hazardous": {
            "battery": {"bin": "Hazardous collection point", "steps": ["Tape terminals", "Do not crush", "Hand to staff"], "why": "Lithium batteries ignite in compactors"},
        },
        "residual": {
            "mixed": {"bin": "Black/Gray bin (Landfill)", "steps": ["Last resort only", "Check other bins first"], "why": "Non-recyclable, non-hazardous waste"},
        },
    }


def get_guidance(predicted_class: str, subtype: str) -> Dict[str, Any]:
    """Get disposal guidance for a classified item."""
    rules = load_rules()
    class_rules = rules.get(predicted_class, {})
    guidance = class_rules.get(subtype, class_rules.get(list(class_rules.keys())[0], {}))
    
    return {
        "bin": guidance.get("bin", "Unknown"),
        "steps": guidance.get("steps", []),
        "why": guidance.get("why", ""),
    }


def get_twin_effect(predicted_class: str, source_node: str = None) -> Dict[str, Any]:
    """Get the effect this scan has on the digital twin."""
    # Simplified: recyclable in right bin = positive, wrong bin = contamination
    return {
        "node": source_node,
        "contamination_delta": 0.0,  # Will be calculated by twin engine
    }