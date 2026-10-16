"""
Twin Events - Scan ingestion, SSE bus
"""
import asyncio
import json
from typing import Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.twin import NodeType, TwinNode, TwinEdge
from app.models.scan import Scan
from app.services.twin.engine import create_initial_state, TwinEngine
from app.services.twin.routing import BIN_NODE_IDS, normalize_bin_name


# SSE event bus
_event_queues: Dict[str, asyncio.Queue] = {}


async def broadcast_event(event_type: str, data: Dict[str, Any]) -> None:
    """Broadcast event to all connected SSE clients."""
    message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    for queue in _event_queues.values():
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            pass


async def create_event_stream() -> AsyncGenerator[str, None]:
    """Create an SSE event stream for a client."""
    queue = asyncio.Queue(maxsize=100)
    client_id = str(id(queue))
    _event_queues[client_id] = queue
    
    try:
        # Send initial connection event
        yield "event: connected\ndata: {}\n\n"
        
        while True:
            message = await queue.get()
            yield message
    finally:
        _event_queues.pop(client_id, None)


async def ingest_scan_event(db: AsyncSession, scan: Scan, confirmed_bin: str = None) -> None:
    """Persist a confirmed scan's source, actual bin, and flow in the twin."""
    confirmed_bin = normalize_bin_name(confirmed_bin)
    bin_id = BIN_NODE_IDS.get(confirmed_bin)
    predicted_class = scan.predicted_class.value if hasattr(scan.predicted_class, "value") else scan.predicted_class
    if bin_id is None:
        raise ValueError(f"Unsupported confirmed bin: {confirmed_bin}")

    if scan.source_node_id is not None:
        source = await db.get(TwinNode, scan.source_node_id)
        if source is None or source.type != NodeType.SOURCE:
            raise ValueError(f"Scan source node {scan.source_node_id} is not a campus source")
        source_config = dict(source.config_json or {})
        source_counts = dict(source_config.get("counts", {}))
        source_counts[predicted_class] = source_counts.get(predicted_class, 0) + 1
        source_config["counts"] = source_counts
        source.config_json = source_config

    bin_node = await db.get(TwinNode, bin_id)
    if bin_node is None:
        raise ValueError(f"Confirmed bin node {bin_id} does not exist")
    bin_config = dict(bin_node.config_json or {})
    bin_counts = dict(bin_config.get("counts", {}))
    bin_counts[predicted_class] = bin_counts.get(predicted_class, 0) + 1
    bin_config["counts"] = bin_counts
    total_in_bin = sum(bin_counts.values())
    capacity = bin_config.get("capacity", 1)
    bin_config["fill_level"] = min(1.0, total_in_bin / capacity) if capacity > 0 else 1.0
    accepts = bin_config.get("accepts", confirmed_bin)
    bin_config["contamination_rate"] = (
        (total_in_bin - bin_counts.get(accepts, 0)) / total_in_bin
        if accepts in ("recyclable", "biodegradable") and total_in_bin
        else 0.0
    )
    bin_node.config_json = bin_config

    if scan.source_node_id is not None:
        result = await db.execute(
            select(TwinEdge).where(TwinEdge.from_id == scan.source_node_id, TwinEdge.to_id == bin_id)
        )
        edge = result.scalar_one_or_none()
        if edge is None:
            edge = TwinEdge(from_id=scan.source_node_id, to_id=bin_id, weight=1.0, route_prob=0.0)
            db.add(edge)
        else:
            edge.weight += 1.0

    await db.commit()
    
    # Broadcast scan.created event
    await broadcast_event("scan.created", {
        "scan_id": scan.id,
        "predicted_class": predicted_class,
        "subtype": scan.subtype,
        "confidence": scan.confidence,
        "source_node_id": scan.source_node_id,
        "confirmed_bin": confirmed_bin,
    })
    
    # Broadcast metrics.updated
    # Get current metrics
    from app.services.twin.graph import get_twin_metrics
    metrics = await get_twin_metrics(db)
    await broadcast_event("metrics.updated", metrics.model_dump(mode="json"))


async def generate_demo_traffic(db: AsyncSession, ticks: int = 10) -> None:
    """Generate demo traffic for the twin."""
    engine = TwinEngine(seed=42)
    state = create_initial_state()
    
    for tick in range(ticks):
        result = engine.run_tick(state)
        
        # Broadcast twin.tick event
        await broadcast_event("twin.tick", {
            "tick": tick,
            "metrics": result["metrics"].model_dump(mode="json") if hasattr(result["metrics"], "model_dump") else result["metrics"],
        })
        
        # Small delay
        await asyncio.sleep(0.5)
    
    # Broadcast final metrics
    await broadcast_event("metrics.updated", result["metrics"].model_dump(mode="json") if hasattr(result["metrics"], "model_dump") else result["metrics"])


async def reset_demo_data(db: AsyncSession) -> None:
    """Reset demo data to initial state."""
    from app.services.twin.graph import seed_twin
    await seed_twin(db)
    await broadcast_event("demo.reset", {"message": "Demo data reset"})