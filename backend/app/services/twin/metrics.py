"""
Twin Metrics - Diversion, contamination, CO2e, pickup cost
"""
import math
from typing import Dict, Any
from app.schemas.twin import MetricsResponse
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scan import Scan
from app.models.twin import NodeType, TwinNode
from app.services.twin.routing import BIN_NODE_IDS, normalize_bin_name


# Emission factors (kg CO2e per kg material)
# Placeholders - replace with EPA WARM citations before demo
EMISSION_FACTORS = {
    "recyclable": {
        "virgin_factor": 2.5,    # kg CO2e/kg virgin material
        "recycled_factor": 0.5,  # kg CO2e/kg recycled material
        "avg_weight_kg": 0.15,   # avg weight per item
    },
    "reusable": {
        "virgin_factor": 8.0,
        "recycled_factor": 0.2,
        "avg_weight_kg": 0.5,
    },
    "biodegradable": {
        "virgin_factor": 1.0,
        "recycled_factor": 0.1,  # composting
        "avg_weight_kg": 0.2,
    },
    "hazardous": {
        "virgin_factor": 5.0,
        "recycled_factor": 1.0,  # proper handling
        "avg_weight_kg": 0.1,
    },
    "residual": {
        "virgin_factor": 0.0,
        "recycled_factor": 0.0,
        "avg_weight_kg": 0.2,
    },
}

# Pickup cost per trip
PICKUP_COST_PER_TRIP = 100.0


def compute_metrics_from_state(state: Dict[str, Any]) -> MetricsResponse:
    """Compute all metrics from current twin state."""
    nodes = state.get("nodes", {})
    
    # Count items at facilities (recovered)
    recovered = {"recyclable": 0, "reusable": 0, "biodegradable": 0, "hazardous": 0, "residual": 0}
    total_generated = {"recyclable": 0, "reusable": 0, "biodegradable": 0, "hazardous": 0, "residual": 0}
    
    # Sum facility throughput (recovered)
    for node_id, node_data in nodes.items():
        if node_data["type"] == "facility":
            throughput = node_data.get("config", {}).get("throughput", {})
            for cls, count in throughput.items():
                if cls in recovered:
                    recovered[cls] += count
    
    # Sum source generation (total)
    for node_id, node_data in nodes.items():
        if node_data["type"] == "source":
            counts = node_data.get("config", {}).get("counts", {})
            for cls, count in counts.items():
                if cls in total_generated:
                    total_generated[cls] += count
    
    # Diversion rate = recovered / total (excluding residual from recovered)
    total_items = sum(total_generated.values())
    recovered_items = sum(recovered[cls] for cls in ["recyclable", "reusable", "biodegradable", "hazardous"])
    diversion_rate = recovered_items / total_items if total_items > 0 else 0.0
    
    # Contamination rate = misrouted / items in recyclable & biodegradable bins
    contamination_rate = compute_contamination_rate(nodes)
    
    # CO2e avoided
    co2e_avoided = compute_co2e_avoided(recovered)
    
    # Pickup cost
    pickup_cost = compute_pickup_cost(nodes)
    
    return MetricsResponse(
        diversion_rate=diversion_rate,
        contamination_rate=contamination_rate,
        co2e_avoided_kg=co2e_avoided,
        pickup_cost=pickup_cost,
        total_items=total_items,
        recovered_items=recovered_items,
        timestamp=datetime.utcnow(),
    )


def compute_contamination_rate(nodes: Dict[int, Dict]) -> float:
    """Compute contamination rate across recyclable and biodegradable bins."""
    total_in_target_bins = 0
    misrouted_in_target_bins = 0
    
    for node_id, node_data in nodes.items():
        if node_data["type"] != "bin":
            continue
        
        config = node_data.get("config", {})
        accepts = config.get("accepts", "")
        counts = config.get("counts", {})
        
        if accepts not in ("recyclable", "biodegradable"):
            continue
        
        bin_total = sum(counts.values())
        if bin_total == 0:
            continue
        
        correct = counts.get(accepts, 0)
        misrouted = bin_total - correct
        
        total_in_target_bins += bin_total
        misrouted_in_target_bins += misrouted
    
    return misrouted_in_target_bins / total_in_target_bins if total_in_target_bins > 0 else 0.0


def compute_co2e_avoided(recovered: Dict[str, int]) -> float:
    """Compute CO2e avoided from recovered materials."""
    total_co2e = 0.0
    
    for cls, count in recovered.items():
        if cls not in EMISSION_FACTORS:
            continue
        
        factors = EMISSION_FACTORS[cls]
        weight = count * factors["avg_weight_kg"]
        avoided_per_kg = factors["virgin_factor"] - factors["recycled_factor"]
        total_co2e += weight * avoided_per_kg
    
    return round(total_co2e, 2)


def compute_pickup_cost(nodes: Dict[int, Dict]) -> float:
    """Estimate pickup cost from collection activity."""
    trips = 0
    
    for node_id, node_data in nodes.items():
        if node_data["type"] == "collection":
            config = node_data.get("config", {})
            # Count non-zero collection events
            # Simplified: assume 1 trip per collection node per schedule
            trips += 1
    
    return trips * PICKUP_COST_PER_TRIP


async def compute_current_metrics(db: AsyncSession) -> MetricsResponse:
    """Compute current metrics from scans and confirmed bin choices in the database."""
    result = await db.execute(select(Scan))
    scans = result.scalars().all()
    confirmed = [scan for scan in scans if normalize_bin_name(scan.confirmed_bin) in {
        "recyclable", "reusable", "biodegradable", "hazardous", "residual"
    }]
    recovered_by_class = {name: 0 for name in EMISSION_FACTORS}
    confirmed_by_bin: Dict[str, int] = {}
    contamination_total = 0
    contaminated_items = 0

    for scan in confirmed:
        confirmed_bin = normalize_bin_name(scan.confirmed_bin)
        confirmed_by_bin[confirmed_bin] = confirmed_by_bin.get(confirmed_bin, 0) + 1
        predicted_class = scan.predicted_class.value if hasattr(scan.predicted_class, "value") else scan.predicted_class
        if confirmed_bin != "residual":
            recovered_by_class[predicted_class] += 1
        if confirmed_bin in ("recyclable", "biodegradable"):
            contamination_total += 1
            if predicted_class != confirmed_bin:
                contaminated_items += 1

    nodes_result = await db.execute(select(TwinNode).where(TwinNode.type == NodeType.BIN))
    capacities = {}
    bin_names_by_id = {node_id: name for name, node_id in BIN_NODE_IDS.items()}
    for node in nodes_result.scalars().all():
        config = node.config_json or {}
        accepts = config.get("accepts") or bin_names_by_id.get(node.id)
        if accepts:
            capacities[normalize_bin_name(accepts)] = max(1, config.get("capacity", 1))

    trips = sum(
        math.ceil(count / capacities.get(bin_name, 1))
        for bin_name, count in confirmed_by_bin.items()
    )
    recovered_items = sum(recovered_by_class.values())
    total_items = len(scans)
    return MetricsResponse(
        diversion_rate=recovered_items / total_items if total_items else 0.0,
        contamination_rate=contaminated_items / contamination_total if contamination_total else 0.0,
        co2e_avoided_kg=compute_co2e_avoided(recovered_by_class),
        pickup_cost=trips * PICKUP_COST_PER_TRIP,
        total_items=total_items,
        recovered_items=recovered_items,
        timestamp=datetime.now(timezone.utc),
    )