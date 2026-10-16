"""
Twin Events - Scan ingestion, SSE bus
"""
import asyncio
import json
from typing import Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.twin import TwinNode, TwinEdge
from app.models.scan import Scan
from app.services.twin.graph import update_node_counts, increment_edge_weight
from app.services.twin.engine import create_initial_state, TwinEngine
from app.services.twin.metrics import compute_metrics_from_state


# SSE event bus
_event_queues: Dict[str, asyncio.Queue] = {}


async def broadcast_event(event_type: str, data: Dict[str, Any]) -> None:
    """Broadcast event to all connected SSE clients."""
    message = json.dumps({"type": event_type, "data": data})
    for queue in _event_queues.values():
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            pass


def create_event_stream() -> AsyncGenerator[str, None]:
    """Create an SSE event stream for a client."""
    queue = asyncio.Queue(maxsize=100)
    client_id = str(id(queue))
    _event_queues[client_id] = queue
    
    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'data': {}})}\n\n"
        
        while True:
            message = await queue.get()
            yield f"data: {message}\n\n"
    finally:
        _event_queues.pop(client_id, None)


async def ingest_scan_event(db: AsyncSession, scan: Scan, confirmed_bin: str = None) -> None:
    """Process a scan event into the twin."""
    # Update source node counts
    if scan.source_node_id:
        await update_node_counts(db, scan.source_node_id, scan.predicted_class, 1)
        
        # Increment edge weight from source to bin
        # Find the bin node from confirmed_bin or predicted class
        bin_map = {
            "recyclable": 10,
            "reusable": 11,
            "biodegradable": 12,
            "hazardous": 13,
            "residual": 14,
        }
        bin_id = bin_map.get(scan.predicted_class, 14)
        if confirmed_bin:
            # Map confirmed bin name to ID
            bin_name_to_id = {
                "Recyclable Bin": 10,
                "Reusable Bin": 11,
                "Biodegradable Bin": 12,
                "Hazardous Bin": 13,
                "Residual Bin": 14,
            }
            bin_id = bin_name_to_id.get(confirmed_bin, bin_id)
        
        await increment_edge_weight(db, scan.source_node_id, bin_id, 1.0)
    
    # Broadcast scan.created event
    await broadcast_event("scan.created", {
        "scan_id": scan.id,
        "predicted_class": scan.predicted_class,
        "subtype": scan.subtype,
        "confidence": scan.confidence,
        "source_node_id": scan.source_node_id,
        "confirmed_bin": confirmed_bin,
    })
    
    # Broadcast metrics.updated
    # Get current metrics
    from app.services.twin.graph import get_twin_metrics
    metrics = await get_twin_metrics(db)
    await broadcast_event("metrics.updated", metrics.model_dump())


async def generate_demo_traffic(db: AsyncSession, ticks: int = 10) -> None:
    """Generate demo traffic for the twin."""
    engine = TwinEngine(seed=42)
    state = create_initial_state()
    
    for tick in range(ticks):
        result = engine.run_tick(state)
        
        # Broadcast twin.tick event
        await broadcast_event("twin.tick", {
            "tick": tick,
            "metrics": result["metrics"].model_dump() if hasattr(result["metrics"], "model_dump") else result["metrics"],
        })
        
        # Small delay
        await asyncio.sleep(0.5)
    
    # Broadcast final metrics
    await broadcast_event("metrics.updated", result["metrics"].model_dump() if hasattr(result["metrics"], "model_dump") else result["metrics"])


async def reset_demo_data(db: AsyncSession) -> None:
    """Reset demo data to initial state."""
    from app.services.twin.graph import seed_twin
    await seed_twin(db)
    await broadcast_event("demo.reset", {"message": "Demo data reset"})