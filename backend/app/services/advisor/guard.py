"""
Advisor Guard - Validate output numbers against input, prevent hallucination
"""
from typing import Dict, Any, List, Optional
import re


def validate_advice_output(advice: Dict[str, Any], input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate that every number in advice output appears in input data.
    Returns validated advice or None if validation fails.
    """
    # Extract all numbers from input
    input_numbers = set()
    _extract_numbers(input_data, input_numbers)
    
    # Check advice numbers
    advice_str = str(advice)
    advice_numbers = _extract_numbers_from_text(advice_str)
    
    # Allow small tolerance for formatting differences
    for num in advice_numbers:
        if not _number_in_input(num, input_numbers):
            print(f"Validation failed: number {num} not in input")
            return None
    
    # Check required fields
    required = ["summary", "issues", "actions", "reuse_ideas", "disclaimer"]
    for field in required:
        if field not in advice:
            print(f"Validation failed: missing field {field}")
            return None
    
    # Validate actions structure
    for action in advice.get("actions", []):
        if not all(k in action for k in ["title", "why", "expected_impact", "effort", "owner"]):
            print("Validation failed: action missing required keys")
            return None
        if action["effort"] not in ["low", "medium", "high"]:
            print(f"Validation failed: invalid effort {action['effort']}")
            return None
        if action["owner"] not in ["residents", "facilities", "management"]:
            print(f"Validation failed: invalid owner {action['owner']}")
            return None
    
    return advice


def _extract_numbers(obj: Any, numbers: set) -> None:
    """Recursively extract all numbers from input data."""
    if isinstance(obj, (int, float)):
        numbers.add(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            _extract_numbers(v, numbers)
    elif isinstance(obj, list):
        for item in obj:
            _extract_numbers(item, numbers)


def _extract_numbers_from_text(text: str) -> List[float]:
    """Extract numbers from text (including percentages, decimals)."""
    # Match numbers: integers, decimals, percentages
    pattern = r'-?\d+\.?\d*%?'
    matches = re.findall(pattern, text)
    numbers = []
    for m in matches:
        if m.endswith('%'):
            try:
                numbers.append(float(m[:-1]) / 100)
            except ValueError:
                pass
        else:
            try:
                numbers.append(float(m))
            except ValueError:
                pass
    return numbers


def _number_in_input(num: float, input_numbers: set, tolerance: float = 0.01) -> bool:
    """Check if a number exists in input (with tolerance)."""
    for in_num in input_numbers:
        if abs(num - in_num) < tolerance:
            return True
        # Also check percentage equivalents
        if abs(num * 100 - in_num) < tolerance:
            return True
        if abs(num - in_num * 100) < tolerance:
            return True
    return False


def sanitize_advice_output(advice: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize advice output for safe rendering."""
    # Ensure strings are safe
    for key in ["summary", "disclaimer"]:
        if key in advice and isinstance(advice[key], str):
            advice[key] = advice[key][:2000]  # Limit length
    
    # Sanitize issues
    if "issues" in advice:
        advice["issues"] = [str(i)[:500] for i in advice["issues"][:10]]
    
    # Sanitize actions
    if "actions" in advice:
        for action in advice["actions"][:10]:
            for key in ["title", "why", "expected_impact"]:
                if key in action and isinstance(action[key], str):
                    action[key] = action[key][:1000]
    
    # Sanitize reuse_ideas
    if "reuse_ideas" in advice:
        advice["reuse_ideas"] = [str(i)[:500] for i in advice["reuse_ideas"][:10]]
    
    return advice