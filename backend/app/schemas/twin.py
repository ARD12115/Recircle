"""
Twin Schemas - Request/Response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TwinNodeResponse(BaseModel):
    id: int
    type: str
    name: str
    config: Dict[str, Any]
    counts: Dict[str, int] = {}
    fill_level: Optional[float] = None
    contamination_rate: Optional[float] = None
    throughput: Optional[float] = None


class TwinEdgeResponse(BaseModel):
    id: int
    from_id: int
    to_id: int
    weight: float
    route_prob: float


class TwinGraphResponse(BaseModel):
    nodes: List[TwinNodeResponse]
    edges: List[TwinEdgeResponse]


class MetricsResponse(BaseModel):
    diversion_rate: float
    contamination_rate: float
    co2e_avoided_kg: float
    pickup_cost: float
    total_items: int
    recovered_items: int
    timestamp: datetime


class TwinResponse(BaseModel):
    graph: TwinGraphResponse
    metrics: MetricsResponse


class SimulateRequest(BaseModel):
    compliance: float = Field(ge=0.0, le=1.0, default=0.6)
    awareness_boost: float = Field(ge=0.0, le=1.0, default=0.0)
    pickup_frequency: float = Field(ge=0.5, le=2.0, default=1.0)
    bins_per_stream: int = Field(ge=1, le=5, default=1)
    facility_yield_override: Optional[Dict[str, float]] = None
    ticks: int = Field(ge=1, le=365, default=30)


class ScenarioResult(BaseModel):
    params: Dict[str, Any]
    metrics: MetricsResponse


class SimulateResponse(BaseModel):
    baseline: ScenarioResult
    scenario: ScenarioResult
    deltas: Dict[str, float]