import pytest
from app.services.advisor.guard import validate_advice_output, sanitize_advice_output


def test_valid_advice_passes():
    """Valid advice with numbers from input should pass."""
    input_data = {
        "metrics": {"diversion_rate": 0.62, "contamination_rate": 0.18},
        "scenario_deltas": {"diversion_rate": 0.12, "contamination_rate": -0.05},
    }
    
    advice = {
        "summary": "System shows 62% diversion.",
        "issues": ["Contamination at 18%"],
        "actions": [{
            "title": "Add signage",
            "why": "Contamination rate of 18% suggests confusion",
            "expected_impact": "Reduce contamination by 3-5 percentage points",
            "effort": "low",
            "owner": "facilities",
        }],
        "reuse_ideas": ["Glass jars as storage"],
        "disclaimer": "Guidance is informational.",
    }
    
    result = validate_advice_output(advice, input_data)
    assert result is not None
    assert result["summary"] == advice["summary"]


def test_invented_number_rejected():
    """Advice with numbers not in input should be rejected."""
    input_data = {
        "metrics": {"diversion_rate": 0.62},
        "scenario_deltas": {},
    }
    
    advice = {
        "summary": "System shows 62% diversion.",
        "issues": [],
        "actions": [{
            "title": "Test",
            "why": "Test",
            "expected_impact": "Increase diversion by 50%",  # 50% not in input
            "effort": "low",
            "owner": "facilities",
        }],
        "reuse_ideas": [],
        "disclaimer": "Test",
    }
    
    result = validate_advice_output(advice, input_data)
    assert result is None


def test_missing_required_fields_rejected():
    """Advice missing required fields should be rejected."""
    input_data = {"metrics": {}}
    
    advice = {
        "summary": "Test",
        "issues": [],
        # missing actions, reuse_ideas, disclaimer
    }
    
    result = validate_advice_output(advice, input_data)
    assert result is None


def test_invalid_effort_rejected():
    """Invalid effort value should be rejected."""
    input_data = {"metrics": {"diversion_rate": 0.62}}
    
    advice = {
        "summary": "Test",
        "issues": [],
        "actions": [{
            "title": "Test",
            "why": "Test",
            "expected_impact": "Increase diversion",
            "effort": "super-easy",  # Invalid
            "owner": "facilities",
        }],
        "reuse_ideas": [],
        "disclaimer": "Test",
    }
    
    result = validate_advice_output(advice, input_data)
    assert result is None


def test_invalid_owner_rejected():
    """Invalid owner value should be rejected."""
    input_data = {"metrics": {"diversion_rate": 0.62}}
    
    advice = {
        "summary": "Test",
        "issues": [],
        "actions": [{
            "title": "Test",
            "why": "Test",
            "expected_impact": "Increase diversion",
            "effort": "low",
            "owner": "random-person",  # Invalid
        }],
        "reuse_ideas": [],
        "disclaimer": "Test",
    }
    
    result = validate_advice_output(advice, input_data)
    assert result is None


def test_sanitize_limits_length():
    """Sanitize should limit string lengths."""
    advice = {
        "summary": "x" * 3000,
        "disclaimer": "y" * 3000,
        "issues": ["z" * 600] * 15,
        "actions": [{
            "title": "a" * 1500,
            "why": "b" * 1500,
            "expected_impact": "c" * 1500,
            "effort": "low",
            "owner": "facilities",
        }] * 15,
        "reuse_ideas": ["d" * 600] * 15,
    }
    
    sanitized = sanitize_advice_output(advice)
    
    assert len(sanitized["summary"]) <= 2000
    assert len(sanitized["disclaimer"]) <= 2000
    assert len(sanitized["issues"]) <= 10
    assert all(len(i) <= 500 for i in sanitized["issues"])
    assert len(sanitized["actions"]) <= 10
    for action in sanitized["actions"]:
        assert len(action["title"]) <= 1000
        assert len(action["why"]) <= 1000
        assert len(action["expected_impact"]) <= 1000
    assert len(sanitized["reuse_ideas"]) <= 10
    assert all(len(i) <= 500 for i in sanitized["reuse_ideas"])