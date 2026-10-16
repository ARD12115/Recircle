import pytest
from app.services.twin.engine import TwinEngine, create_initial_state
from app.schemas.twin import SimulateRequest


@pytest.fixture
def initial_state():
    return create_initial_state()


@pytest.fixture
def engine():
    return TwinEngine(seed=42)


def test_twin_determinism(initial_state, engine):
    """Same seed should produce identical results."""
    params = SimulateRequest(compliance=0.6, ticks=10)
    
    result1 = engine.run_simulation(initial_state, params)
    result2 = engine.run_simulation(initial_state, params)
    
    assert result1.baseline.metrics.diversion_rate == result2.baseline.metrics.diversion_rate
    assert result1.scenario.metrics.diversion_rate == result2.scenario.metrics.diversion_rate


def test_twin_metrics_computation(initial_state, engine):
    """Test metric calculations on known state."""
    result = engine.run_tick(initial_state, compliance=1.0)  # Perfect compliance
    
    # With perfect compliance, contamination should be 0
    assert result["metrics"].contamination_rate == 0.0
    # Diversion should be high
    assert result["metrics"].diversion_rate > 0.5


def test_compliance_effect(initial_state, engine):
    """Higher compliance should improve diversion."""
    params_low = SimulateRequest(compliance=0.3, ticks=20)
    params_high = SimulateRequest(compliance=0.9, ticks=20)
    
    result_low = engine.run_simulation(initial_state, params_low)
    result_high = engine.run_simulation(initial_state, params_high)
    
    assert result_high.scenario.metrics.diversion_rate >= result_low.scenario.metrics.diversion_rate


def test_contamination_effect(initial_state, engine):
    """Lower compliance should increase contamination."""
    params_low = SimulateRequest(compliance=0.3, ticks=20)
    params_high = SimulateRequest(compliance=0.9, ticks=20)
    
    result_low = engine.run_simulation(initial_state, params_low)
    result_high = engine.run_simulation(initial_state, params_high)
    
    assert result_low.scenario.metrics.contamination_rate >= result_high.scenario.metrics.contamination_rate


def test_awareness_boost(initial_state, engine):
    """Awareness boost should act like compliance increase."""
    params_base = SimulateRequest(compliance=0.6, awareness_boost=0.0, ticks=20)
    params_boost = SimulateRequest(compliance=0.6, awareness_boost=0.2, ticks=20)
    
    result_base = engine.run_simulation(initial_state, params_base)
    result_boost = engine.run_simulation(initial_state, params_boost)
    
    assert result_boost.scenario.metrics.diversion_rate >= result_base.scenario.metrics.diversion_rate


def test_pickup_frequency(initial_state, engine):
    """Higher pickup frequency should reduce fill levels but increase cost."""
    params_low = SimulateRequest(pickup_frequency=0.5, ticks=20)
    params_high = SimulateRequest(pickup_frequency=2.0, ticks=20)
    
    result_low = engine.run_simulation(initial_state, params_low)
    result_high = engine.run_simulation(initial_state, params_high)
    
    # Higher frequency = more trips = higher cost
    assert result_high.scenario.metrics.pickup_cost >= result_low.scenario.metrics.pickup_cost


def test_scenario_deltas_structure(initial_state, engine):
    """Verify deltas contain all expected keys."""
    params = SimulateRequest(compliance=0.8, ticks=15)
    result = engine.run_simulation(initial_state, params)
    
    expected_keys = {"diversion_rate", "contamination_rate", "co2e_avoided_kg", "pickup_cost"}
    assert set(result.deltas.keys()) == expected_keys
    assert all(isinstance(v, (int, float)) for v in result.deltas.values())