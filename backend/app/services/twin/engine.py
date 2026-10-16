"""
Twin Engine - Simulation tick loop
"""
import random
import json
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.twin import TwinNode, TwinEdge, TwinSnapshot
from app.schemas.twin import MetricsResponse, SimulateRequest, SimulateResponse, ScenarioResult
from app.services.twin.metrics import compute_metrics_from_state


class TwinEngine:
    """Digital Twin simulation engine."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
    
    def reset_rng(self):
        self.rng = random.Random(self.seed)
    
    def run_tick(self, state: Dict[str, Any], compliance: float = 0.6, 
                 awareness_boost: float = 0.0, pickup_frequency: float = 1.0,
                 bins_per_stream: int = 1, facility_yield_override: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Run one simulation tick (one day).
        Returns updated state and metrics.
        """
        # 1. Generate items per source from waste-mix distribution
        items_generated = self._generate_items(state)
        
        # 2. Route items to bins (with compliance probability)
        items_routed = self._route_to_bins(items_generated, compliance, awareness_boost)
        
        # 3. Update bin contamination
        self._update_contamination(state, items_routed)
        
        # 4. Collection (scheduled)
        collected = self._run_collection(state, pickup_frequency)
        
        # 5. Facility processing
        processed = self._process_at_facilities(state, collected, facility_yield_override)
        
        # 6. Compute metrics
        metrics = compute_metrics_from_state(state)
        
        return {
            "state": state,
            "metrics": metrics,
            "items_generated": items_generated,
            "items_routed": items_routed,
            "collected": collected,
            "processed": processed,
        }
    
    def _generate_items(self, state: Dict[str, Any]) -> Dict[int, Dict[str, int]]:
        """Generate items at each source node."""
        items = {}
        for node_id, node_data in state["nodes"].items():
            if node_data["type"] != "source":
                continue
            
            config = node_data.get("config", {})
            waste_mix = config.get("waste_mix", {})
            daily_items = config.get("daily_items", 100)
            
            # Sample items from multinomial distribution
            classes = list(waste_mix.keys())
            probs = list(waste_mix.values())
            
            node_items = {cls: 0 for cls in classes}
            for _ in range(daily_items):
                cls = self.rng.choices(classes, weights=probs, k=1)[0]
                node_items[cls] += 1
            
            items[node_id] = node_items
            
            # Update node counts
            counts = node_data.setdefault("counts", {})
            for cls, count in node_items.items():
                counts[cls] = counts.get(cls, 0) + count
        
        return items
    
    def _route_to_bins(self, items_generated: Dict[int, Dict[str, int]], 
                       compliance: float, awareness_boost: float) -> Dict[int, Dict[str, Dict[int, int]]]:
        """
        Route items from sources to bins.
        Returns: {source_id: {true_class: {bin_id: count}}}
        """
        effective_compliance = min(1.0, compliance + awareness_boost)
        routed = {}
        
        # Bin mapping (simplified - in reality from edges)
        bin_map = {
            "recyclable": 10,
            "reusable": 11,
            "biodegradable": 12,
            "hazardous": 13,
            "residual": 14,
        }
        
        for source_id, class_counts in items_generated.items():
            routed[source_id] = {}
            for true_class, count in class_counts.items():
                routed[source_id][true_class] = {}
                correct_bin = bin_map.get(true_class, 14)
                
                for _ in range(count):
                    if self.rng.random() < effective_compliance:
                        # Correct bin
                        bin_id = correct_bin
                    else:
                        # Wrong bin - pick random other bin
                        other_bins = [b for b in bin_map.values() if b != correct_bin]
                        bin_id = self.rng.choice(other_bins)
                    
                    routed[source_id][true_class][bin_id] = routed[source_id][true_class].get(bin_id, 0) + 1
        
        return routed
    
    def _update_contamination(self, state: Dict[str, Any], items_routed: Dict) -> None:
        """Update bin contamination rates."""
        for source_id, class_routes in items_routed.items():
            for true_class, bin_counts in class_routes.items():
                for bin_id, count in bin_counts.items():
                    bin_node = state["nodes"].get(bin_id)
                    if not bin_node or bin_node["type"] != "bin":
                        continue
                    
                    config = bin_node.setdefault("config", {})
                    counts = config.setdefault("counts", {})
                    counts[true_class] = counts.get(true_class, 0) + count
                    
                    # Calculate contamination rate
                    total = sum(counts.values())
                    if total > 0:
                        # Contamination = non-matching items / total in recyclable & biodegradable bins
                        bin_type = config.get("accepts", "recyclable")
                        if bin_type in ("recyclable", "biodegradable"):
                            correct = counts.get(bin_type, 0)
                            contamination = (total - correct) / total
                            config["contamination_rate"] = contamination
                        else:
                            config["contamination_rate"] = 0.0
                    
                    # Fill level
                    capacity = config.get("capacity", 500)
                    config["fill_level"] = min(1.0, total / capacity)
    
    def _run_collection(self, state: Dict[str, Any], pickup_frequency: float) -> Dict[int, Dict[str, int]]:
        """Run collection routes on schedule."""
        collected = {}
        
        for node_id, node_data in state["nodes"].items():
            if node_data["type"] != "bin":
                continue
            
            config = node_data.get("config", {})
            schedule_days = config.get("schedule_days", 2)
            
            # Simplified: collect every tick * pickup_frequency / schedule_days
            if self.rng.random() < (pickup_frequency / schedule_days):
                counts = config.get("counts", {})
                if any(counts.values()):
                    collected[node_id] = counts.copy()
                    # Empty bin
                    config["counts"] = {k: 0 for k in counts}
                    config["fill_level"] = 0.0
                    config["contamination_rate"] = 0.0
        
        return collected
    
    def _process_at_facilities(self, state: Dict[str, Any], collected: Dict[int, Dict[str, int]],
                               facility_yield_override: Dict[str, float] = None) -> Dict[int, Dict[str, int]]:
        """Process collected items at facilities."""
        processed = {}
        
        # Map bins to facilities via edges
        bin_to_facility = {
            10: 30,  # Recyclable -> Recycling
            11: 33,  # Reusable -> Reuse & Donation
            12: 31,  # Biodegradable -> Composting
            13: 32,  # Hazardous -> Hazardous Handling
            14: 34,  # Residual -> Landfill
        }
        
        for bin_id, items in collected.items():
            facility_id = bin_to_facility.get(bin_id)
            if not facility_id:
                continue
            
            facility = state["nodes"].get(facility_id)
            if not facility:
                continue
            
            config = facility.get("config", {})
            throughput = config.setdefault("throughput", {})
            
            # Determine yield based on contamination
            bin_node = state["nodes"].get(bin_id)
            contamination = bin_node.get("config", {}).get("contamination_rate", 0) if bin_node else 0
            
            yield_clean = config.get("yield_clean", 0.85)
            yield_contaminated = config.get("yield_contaminated", 0.55)
            
            if facility_yield_override and facility_id in facility_yield_override:
                yield_clean = facility_yield_override[facility_id]
                yield_contaminated = yield_clean
            
            effective_yield = yield_clean * (1 - contamination) + yield_contaminated * contamination
            
            for cls, count in items.items():
                recovered = int(count * effective_yield)
                throughput[cls] = throughput.get(cls, 0) + recovered
                processed.setdefault(facility_id, {})[cls] = recovered
        
        return processed
    
    def run_simulation(self, initial_state: Dict[str, Any], params: SimulateRequest) -> SimulateResponse:
        """Run full simulation for baseline and scenario."""
        # Baseline (default params)
        baseline_state = self._deep_copy_state(initial_state)
        self.reset_rng()
        baseline_metrics = None
        
        for _ in range(params.ticks):
            result = self.run_tick(
                baseline_state,
                compliance=0.6,  # Baseline compliance
                awareness_boost=0.0,
                pickup_frequency=1.0,
                bins_per_stream=1,
                facility_yield_override=None,
            )
            baseline_metrics = result["metrics"]
        
        # Scenario
        scenario_state = self._deep_copy_state(initial_state)
        self.reset_rng()
        scenario_metrics = None
        
        for _ in range(params.ticks):
            result = self.run_tick(
                scenario_state,
                compliance=params.compliance,
                awareness_boost=params.awareness_boost,
                pickup_frequency=params.pickup_frequency,
                bins_per_stream=params.bins_per_stream,
                facility_yield_override=params.facility_yield_override,
            )
            scenario_metrics = result["metrics"]
        
        # Compute deltas
        deltas = {}
        if baseline_metrics and scenario_metrics:
            for key in ["diversion_rate", "contamination_rate", "co2e_avoided_kg", "pickup_cost"]:
                b = getattr(baseline_metrics, key, 0)
                s = getattr(scenario_metrics, key, 0)
                deltas[key] = s - b
        
        return SimulateResponse(
            baseline=ScenarioResult(params={"compliance": 0.6}, metrics=baseline_metrics),
            scenario=ScenarioResult(params=params.model_dump(), metrics=scenario_metrics),
            deltas=deltas,
        )
    
    def _deep_copy_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Deep copy state for simulation isolation."""
        import copy
        return copy.deepcopy(state)


def create_initial_state() -> Dict[str, Any]:
    """Create initial twin state from seed."""
    from app.services.twin.graph import load_twin_seed
    seed = load_twin_seed()
    
    state = {"nodes": {}, "edges": {}}
    
    for node_data in seed["nodes"]:
        state["nodes"][node_data["id"]] = {
            "id": node_data["id"],
            "type": node_data["type"],
            "name": node_data["name"],
            "config": node_data["config"].copy(),
        }
    
    for edge_data in seed["edges"]:
        edge_id = f"{edge_data['from_id']}->{edge_data['to_id']}"
        state["edges"][edge_id] = {
            "from_id": edge_data["from_id"],
            "to_id": edge_data["to_id"],
            "weight": edge_data["weight"],
            "route_prob": edge_data["route_prob"],
        }
    
    return state