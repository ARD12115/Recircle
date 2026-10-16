"""
Scan Schemas - Request/Response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Top3Item(BaseModel):
    class_name: str
    confidence: float


class Guidance(BaseModel):
    bin: str
    steps: List[str]
    why: str
    twin_effect: dict


class ScanResponse(BaseModel):
    scan_id: str
    predicted_class: Literal["recyclable", "reusable", "biodegradable", "hazardous", "residual", "unsure"]
    subtype: str
    confidence: float
    top3: List[Top3Item]
    guidance: Guidance
    latency_ms: int


class ScanHistoryItem(BaseModel):
    id: int
    created_at: datetime
    predicted_class: str
    subtype: str
    confidence: float
    source_node_id: Optional[int]
    confirmed_bin: Optional[str]
    image_ref: Optional[str]
    latency_ms: int


class ScanHistoryResponse(BaseModel):
    scans: List[ScanHistoryItem]
    total: int
    page: int
    page_size: int


class ScanConfirmationRequest(BaseModel):
    confirmed_bin: Literal["recyclable", "reusable", "biodegradable", "hazardous", "residual"]


class ScanConfirmationResponse(BaseModel):
    scan_id: str
    confirmed_bin: str