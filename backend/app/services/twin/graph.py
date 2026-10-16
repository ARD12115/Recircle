"""
Twin Graph - Nodes, edges, state
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.twin import TwinNode, TwinEdge
from app.schemas.twin import TwinNodeResponse, TwinEdgeResponse, TwinGraphResponse, MetricsResponse


_seed_cache = None


def load_twin_seed() -> Dict[str, Any]:
    global _seed_cache
    if _seed_cache is None:
        seed_path = Path(__file__).parent.parent.parent / "data" / "twin_seed.json"
        if seed_path.exists():
            with open(seed_path) as f:
                _seed_cache = json.load(f)
        else:
            _seed_cache = get_default_seed()
    return _seed_cache


def get_default_seed() -> Dict[str, Any]:
    """Default campus topology."""
    return {
        "nodes": [
            {"id": 1, "type": "source", "name": "Hostel A", "config": {"waste_mix": {"recyclable": 0.3, "reusable": 0.05, "biodegradable": 0.4, "hazardous": 0.02, "residual": 0.23}, "daily_items": 200}},
            {"id": 2, "type": "source", "name": "Hostel B", "config": {"waste_mix": {"recyclable": 0.25, "reusable": 0.05, "biodegradable": 0.45, "hazardous": 0.01, "residual": 0.24}, "daily_items": 180}},
            {"id": 3, "type": "source", "name": "Canteen", "config": {"waste_mix": {"recyclable": 0.2, "reusable": 0.02, "biodegradable": 0.6, "hazardous": 0.01, "residual": 0.17}, "daily_items": 300}},
            {"id": 4, "type": "source", "name": "Library", "config": {"waste_mix": {"recyclable": 0.5, "reusable": 0.02, "biodegradable": 0.1, "hazardous": 0.01, "residual": 0.37}, "daily_items": 80}},
            {"id": 5, "type": "source", "name": "Dept Blocks", "config": {"waste_mix": {"recyclable": 0.4, "reusable": 0.03, "biodegradable": 0.15, "hazardous": 0.02, "residual": 0.4}, "daily_items": 250}},
            {"id": 10, "type": "bin", "name": "Recyclable Bin", "config": {"capacity": 500, "contamination_threshold": 0.15}},
            {"id": 11, "type": "bin", "name": "Reusable Bin", "config": {"capacity": 200, "contamination_threshold": 0.1}},
            {"id": 12, "type": "bin", "name": "Biodegradable Bin", "config": {"capacity": 600, "contamination_threshold": 0.1}},
            {"id": 13, "type": "bin", "name": "Hazardous Bin", "config": {"capacity": 50, "contamination_threshold": 0.0}},
            {"id": 14, "type": "bin", "name": "Residual Bin", "config": {"capacity": 1000, "contamination_threshold": 1.0}},
            {"id": 20, "type": "collection", "name": "Collection Route 1", "config": {"schedule_days": 2, "truck_capacity": 1000}},
            {"id": 21, "type": "collection", "name": "Collection Route 2", "config": {"schedule_days": 3, "truck_capacity": 1000}},
            {"id": 30, "type": "facility", "name": "Recycling Facility", "config": {"yield_clean": 0.85, "yield_contaminated": 0.55, "cost_per_trip": 150}},
            {"id": 31, "type": "facility", "name": "Composting Facility", "config": {"yield_clean": 0.9, "yield_contaminated": 0.6, "cost_per_trip": 100}},
            {"id": 32, "type": "facility", "name": "Hazardous Handling", "config": {"yield_clean": 0.95, "yield_contaminated": 0.95, "cost_per_trip": 500}},
            {"id": 33, "type": "facility", "name": "Reuse & Donation", "config": {"yield_clean": 0.8, "yield_contaminated": 0.4, "cost_per_trip": 80}},
            {"id": 34, "type": "facility", "name": "Landfill", "config": {"yield_clean": 0.0, "yield_contaminated": 0.0, "cost_per_trip": 50}},
        ],
        "edges": [
            # Sources to bins (with routing probabilities)
            {"from_id": 1, "to_id": 10, "weight": 60, "route_prob": 0.6},
            {"from_id": 1, "to_id": 11, "weight": 10, "route_prob": 0.05},
            {"from_id": 1, "to_id": 12, "weight": 80, "route_prob": 0.4},
            {"from_id": 1, "to_id": 13, "weight": 4, "route_prob": 0.02},
            {"from_id": 1, "to_id": 14, "weight": 46, "route_prob": 0.23},
            {"from_id": 2, "to_id": 10, "weight": 45, "route_prob": 0.6},
            {"from_id": 2, "to_id": 11, "weight": 9, "route_prob": 0.05},
            {"from_id": 2, "to_id": 12, "weight": 81, "route_prob": 0.45},
            {"from_id": 2, "to_id": 13, "weight": 2, "route_prob": 0.01},
            {"from_id": 2, "to_id": 14, "weight": 43, "route_prob": 0.24},
            {"from_id": 3, "to_id": 10, "weight": 60, "route_prob": 0.6},
            {"from_id": 3, "to_id": 11, "weight": 6, "route_prob": 0.02},
            {"from_id": 3, "to_id": 12, "weight": 180, "route_prob": 0.6},
            {"from_id": 3, "to_id": 13, "weight": 3, "route_prob": 0.01},
            {"from_id": 3, "to_id": 14, "weight": 51, "route_prob": 0.17},
            {"from_id": 4, "to_id": 10, "weight": 40, "route_prob": 0.6},
            {"from_id": 4, "to_id": 11, "weight": 2, "route_prob": 0.02},
            {"from_id": 4, "to_id": 12, "weight": 8, "route_prob": 0.1},
            {"from_id": 4, "to_id": 13, "weight": 1, "route_prob": 0.01},
            {"from_id": 4, "to_id": 14, "weight": 29, "route_prob": 0.27},
            {"from_id": 5, "to_id": 10, "weight": 100, "route_prob": 0.6},
            {"from_id": 5, "to_id": 11, "weight": 8, "route_prob": 0.03},
            {"from_id": 5, "to_id": 12, "weight": 38, "route_prob": 0.15},
            {"from_id": 5, "to_id": 13, "weight": 5, "route_prob": 0.02},
            {"from_id": 5, "to_id": 14, "weight": 99, "route_prob": 0.4},
            # Bins to collection
            {"from_id": 10, "to_id": 20, "weight": 0, "route_prob": 0.6},
            {"from_id": 11, "to_id": 20, "weight": 0, "route_prob": 0.6},
            {"from_id": 12, "to_id": 20, "weight": 0, "route_prob": 0.6},
            {"from_id": 13, "to_id": 21, "weight": 0, "route_prob": 1.0},
            {"from_id": 14, "to_id": 20, "weight": 0, "route_prob": 0.4},
            {"from_id": 14, "to_id": 21, "weight": 0, "route_prob": 0.6},
            # Collection to facilities
            {"from_id": 20, "to_id": 30, "weight": 0, "route_prob": 0.5},
            {"from_id": 20, "to_id": 31, "weight": 0, "route_prob": 0.3},
            {"from_id": 20, "to_id": 33, "weight": 0, "route_prob": 0.1},
            {"from_id": 20, "to_id": 34, "weight": 0, "route_prob": 0.1},
            {"from_id": 21, "to_id": 32, "weight": 0, "route_prob": 0.5},
            {"from_id": 21, "to_id": 34, "weight": 0, "route_prob": 0.5},
        ],
    }


async def seed_twin(db: AsyncSession) -> None:
    """Seed database with twin topology if empty."""
    result = await db.execute(select(TwinNode.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # Already seeded
    
    seed = load_twin_seed()
    
    # Create nodes
    for node_data in seed["nodes"]:
        node = TwinNode(
            id=node_data["id"],
            type=node_data["type"],
            name=node_data["name"],
            config_json=node_data["config"],
        )
        db.add(node)
    
    # Create edges
    for edge_data in seed["edges"]:
        edge = TwinEdge(
            from_id=edge_data["from_id"],
            to_id=edge_data["to_id"],
            weight=edge_data["weight"],
            route_prob=edge_data["route_prob"],
        )
        db.add(edge)
    
    await db.commit()


async def get_twin_graph(db: AsyncSession) -> TwinGraphResponse:
    """Get full twin graph with current state."""
    # Get nodes
    nodes_result = await db.execute(select(TwinNode))
    nodes = nodes_result.scalars().all()
    
    # Get edges
    edges_result = await db.execute(select(TwinEdge))
    edges = edges_result.scalars().all()
    
    # Build response
    node_responses = []
    for node in nodes:
        counts = node.config_json.get("counts", {}) if node.config_json else {}
        node_responses.append(TwinNodeResponse(
            id=node.id,
            type=node.type.value,
            name=node.name,
            config=node.config_json or {},
            counts=counts,
            fill_level=node.config_json.get("fill_level") if node.config_json else None,
            contamination_rate=node.config_json.get("contamination_rate") if node.config_json else None,
            throughput=node.config_json.get("throughput") if node.config_json else None,
        ))
    
    edge_responses = [
        TwinEdgeResponse(
            id=edge.id,
            from_id=edge.from_id,
            to_id=edge.to_id,
            weight=edge.weight,
            route_prob=edge.route_prob,
        )
        for edge in edges
    ]
    
    return TwinGraphResponse(nodes=node_responses, edges=edge_responses)


async def get_twin_metrics(db: AsyncSession) -> MetricsResponse:
    """Get current twin metrics."""
    # In a real implementation, this would compute from latest snapshot
    # For now, return computed values from engine
    from app.services.twin.metrics import compute_current_metrics
    return await compute_current_metrics(db)


async def update_node_counts(db: AsyncSession, node_id: int, class_name: str, count: int = 1) -> None:
    """Update item counts for a node."""
    result = await db.execute(select(TwinNode).where(TwinNode.id == node_id))
    node = result.scalar_one_or_none()
    
    if node:
        config = node.config_json or {}
        counts = config.get("counts", {})
        counts[class_name] = counts.get(class_name, 0) + count
        config["counts"] = counts
        node.config_json = config
        await db.commit()


async def increment_edge_weight(db: AsyncSession, from_id: int, to_id: int, amount: float = 1.0) -> None:
    """Increment flow weight on an edge."""
    result = await db.execute(
        select(TwinEdge).where(TwinEdge.from_id == from_id, TwinEdge.to_id == to_id)
    )
    edge = result.scalar_one_or_none()
    
    if edge:
        edge.weight += amount
        await db.commit()