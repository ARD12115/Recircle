"""
Twin Generator - Demo traffic generator
"""
import asyncio
import random

from app.models.scan import Scan
from app.services.twin.engine import TwinEngine, create_initial_state
from app.services.twin.events import broadcast_event
from app.services.twin.graph import update_node_counts, increment_edge_weight
from app.core.logging import get_logger


logger = get_logger(__name__)


class DemoTrafficGenerator:
    """Generates realistic demo traffic for the twin."""
    
    def __init__(self, seed: int = 42):
        self.engine = TwinEngine(seed=seed)
        self.running = False
        self.task = None
    
    async def start(self, interval: float = 2.0):
        """Start generating demo traffic."""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_loop(interval))
    
    async def stop(self):
        """Stop generating demo traffic."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
    
    async def _run_loop(self, interval: float):
        """Main loop for demo traffic."""
        from app.db.session import async_session_maker
        from app.services.twin.graph import seed_twin

        state = create_initial_state()
        
        # Source nodes
        source_nodes = [1, 2, 3, 4, 5]  # Hostel A, Hostel B, Canteen, Library, Dept Blocks
        class_choices = ["recyclable", "reusable", "biodegradable", "hazardous", "residual"]

        async with async_session_maker() as seed_db:
            await seed_twin(seed_db)
        
        while self.running:
            try:
                scan_events = []
                async with async_session_maker() as db:
                    for _ in range(random.randint(1, 3)):
                        source_id = random.choice(source_nodes)
                        predicted_class = random.choices(
                            class_choices,
                            weights=[0.3, 0.05, 0.4, 0.02, 0.23],
                            k=1,
                        )[0]
                        scan = Scan(
                            user_id=None,
                            predicted_class=predicted_class,
                            subtype="demo",
                            confidence=random.uniform(0.7, 0.99),
                            source_node_id=source_id,
                            confirmed_bin=None,
                            latency_ms=random.randint(200, 500),
                        )
                        db.add(scan)
                        await db.flush()

                        await update_node_counts(db, source_id, predicted_class, 1)
                        bin_id = {
                            "recyclable": 10,
                            "reusable": 11,
                            "biodegradable": 12,
                            "hazardous": 13,
                            "residual": 14,
                        }.get(predicted_class, 14)
                        await increment_edge_weight(db, source_id, bin_id, 1.0)

                        scan_events.append({
                            "scan_id": scan.id,
                            "predicted_class": predicted_class,
                            "subtype": "demo",
                            "confidence": scan.confidence,
                            "source_node_id": source_id,
                            "confirmed_bin": None,
                        })
                    await db.commit()

                for event in scan_events:
                    await broadcast_event("scan.created", event)
                
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
                logger.exception("Demo traffic generation failed", error=str(e))
                await asyncio.sleep(interval)


# Global instance
demo_generator = DemoTrafficGenerator()