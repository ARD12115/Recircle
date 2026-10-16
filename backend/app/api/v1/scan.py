"""
Scan Endpoint - POST /scan, GET /scans
"""
import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.security import get_current_user, get_guest_user
from app.core.rate_limit import scan_limiter
from app.core.logging import get_logger, audit_log
from app.db.session import get_db
from app.models.scan import Scan, WasteClass
from app.models.user import User
from app.schemas.scan import ScanResponse, ScanHistoryResponse, ScanHistoryItem
from app.services.vision.preprocess import validate_upload, process_image
from app.services.vision.classifier import predict, get_model_info, load_model
from app.services.vision.fallback import zero_shot_classify, unsure_response
from app.services.vision.guidance import get_guidance, get_twin_effect
from app.services.twin.events import ingest_scan_event

router = APIRouter()
logger = get_logger(__name__)


@router.post("", response_model=ScanResponse)
@scan_limiter.limit("10/minute")
async def scan_item(
    request: Request,
    file: UploadFile = File(...),
    source_node_id: Optional[int] = Form(None),
    confirmed_bin: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_guest_user),  # Guest can scan
):
    """Classify an uploaded waste image."""
    start_time = time.time()
    scan_id = str(uuid.uuid4())[:8]
    
    # Validate upload
    file_bytes = await file.read()
    validate_upload(file.content_type, len(file_bytes))
    
    # Process image (strip EXIF, resize, re-encode)
    image = process_image(file_bytes)
    
    # Ensure model loaded
    if not get_model_info()["loaded"]:
        load_model()
    
    # Primary classification
    predicted_class, subtype, confidence, top3 = predict(image)
    
    # Low confidence handling
    if confidence < settings.CONFIDENCE_THRESHOLD:
        # Try fallback
        fallback_result = await zero_shot_classify(image)
        if fallback_result:
            predicted_class, subtype, confidence, top3 = fallback_result
        else:
            # Return unsure response
            hazardous_prob = next((p for c, p in top3 if c == "hazardous"), 0.0)
            unsure = unsure_response(hazardous_prob)
            latency_ms = int((time.time() - start_time) * 1000)
            return ScanResponse(
                scan_id=scan_id,
                predicted_class=unsure["predicted_class"],
                subtype=unsure["subtype"],
                confidence=unsure["confidence"],
                top3=[{"class_name": c, "confidence": p} for c, p in unsure["top3"]],
                guidance=unsure["guidance"],
                latency_ms=latency_ms,
            )
    
    # Get guidance
    guidance_data = get_guidance(predicted_class, subtype)
    twin_effect = get_twin_effect(predicted_class, source_node_id)
    guidance_data["twin_effect"] = twin_effect
    
    # Build top3 response
    top3_response = [{"class_name": c, "confidence": p} for c, p in top3]
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Save scan to database
    scan = Scan(
        user_id=user.get("sub") if not user.get("demo") else None,
        predicted_class=predicted_class,
        subtype=subtype,
        confidence=confidence,
        top3=str(top3_response),
        source_node_id=source_node_id,
        confirmed_bin=confirmed_bin,
        latency_ms=latency_ms,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Ingest into twin
    await ingest_scan_event(db, scan, confirmed_bin)
    
    audit_log("scan_completed", user_id=user.get("sub"), predicted_class=predicted_class, confidence=confidence)
    
    return ScanResponse(
        scan_id=scan_id,
        predicted_class=predicted_class,
        subtype=subtype,
        confidence=confidence,
        top3=top3_response,
        guidance=guidance_data,
        latency_ms=latency_ms,
    )


@router.get("", response_model=ScanHistoryResponse)
async def get_scan_history(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),  # Requires auth
):
    """Get authenticated user's scan history."""
    user_id = int(user["sub"])
    
    # Count total
    count_result = await db.execute(select(Scan).where(Scan.user_id == user_id))
    total = len(count_result.scalars().all())
    
    # Paginated query
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == user_id)
        .order_by(desc(Scan.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    scans = result.scalars().all()
    
    return ScanHistoryResponse(
        scans=[
            ScanHistoryItem(
                id=s.id,
                created_at=s.created_at,
                predicted_class=s.predicted_class.value if hasattr(s.predicted_class, 'value') else s.predicted_class,
                subtype=s.subtype,
                confidence=s.confidence,
                source_node_id=s.source_node_id,
                confirmed_bin=s.confirmed_bin,
                image_ref=s.image_ref,
                latency_ms=s.latency_ms,
            )
            for s in scans
        ],
        total=total,
        page=page,
        page_size=page_size,
    )