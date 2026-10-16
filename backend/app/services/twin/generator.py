"""
Twin Generator - Demo traffic generator
"""
import asyncio
import random
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.twin import TwinNode
from app.models.scan import Scan, WasteClass
from app.services.twin.engine import TwinEngine, create_initial_state
from app.services.twin.events import broadcast_event
from app.services.twin.graph import update_node_counts, increment_edge_weight


class DemoTrafficGenerator:
    """Generates realistic demo traffic for the twin."""
    
    def __init__(self, seed: int = 42):
        self.engine = TwinEngine(seed=seed)
        self.running = False
        self.task = None
    
    async def start(self, db: AsyncSession, interval: float = 2.0):
        """Start generating demo traffic."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_loop(db, interval))
    
    async def stop(self):
        """Stop generating demo traffic."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
    
    async def _run_loop(self, db: AsyncSession, interval: float):
        """Main loop for demo traffic."""
        state = create_initial_state()
        
        # Source nodes
        source_nodes = [1, 2, 3, 4, 5]  # Hostel A, Hostel B, Canteen, Library, Dept Blocks
        class_choices = ["recyclable", "reusable", "biodegradable", "hazardous", "residual"]
        
        while self.running:
            try:
                # Simulate a few random scans
                for _ in range(random.randint(1, 3)):
                    source_id = random.choice(source_nodes)
                    predicted_class = random.choices(
                        class_choices,
                        weights=[0.3, 0.05, 0.4, 0.02, 0.23],
                        k=1
                    )[0]
                    
                    # Create a scan record
                    scan = Scan(
                        user_id=None,  # Demo scan
                        predicted_class=predicted_class,
                        subtype="demo",
                        confidence=random.uniform(0.7, 0.99),
                        source_node_id=source_id,
                        confirmed_bin=None,
                        latency_ms=random.randint(200, 500),
                    )
                    db.add(scan)
                    await db.commit()
                    await db.refresh(scan)
                    
                    # Ingest into twin
                    await update_node_counts(db, source_id, predicted_class, 1)
                    
                    # Bin mapping
                    bin_map = {
                        "recyclable": 10,
                        "reusable": 11,
                        "biodegradable": 12,
                        "hazardous": 13,
                        "residual": 14,
                    }
                    bin_id = bin_map.get(predicted_class, 14)
                    await increment_edge_weight(db, source_id, bin_id, 1.0)
                    
                    # Broadcast
                    await broadcast_event("scan.created", {
                        "scan_id": scan.id,
                        "predicted_class": predicted_class,
                        "subtype": "demo",
                        "confidence": scan.confidence,
                        "source_node_id": source_id,
                        "confirmed_bin": None,
                    })
                
                # Run simulation tick periodically
                if random.random() < 0.3:
                    result = self.engine.run_tick(state)
                    await broadcast_event("twin.tick", {
                        "tick": result.get("tick", 0),
                        "metrics": result["metrics"].model_dump() if hasattr(result["metrics"], "model_dump") else result["metrics"],
                    })
                    
                    # Broadcast metrics
                    await broadcast_event("metrics.updated", result["metrics"].model_dump() if hasattr(result["metrics"], "model_dump") else result["metrics"])
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Demo traffic error: {e}")
                await asyncio.sleep(interval)


# Global instance
demo_generator = DemoTrafficGenerator()