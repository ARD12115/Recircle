"""Scan history endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.scan import Scan
from app.schemas.scan import ScanHistoryItem, ScanHistoryResponse

router = APIRouter()


@router.get("", response_model=ScanHistoryResponse)
async def get_scan_history(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get the authenticated user's paginated scan history."""
    user_id = int(user["sub"])
    count_result = await db.execute(select(Scan).where(Scan.user_id == user_id))
    total = len(count_result.scalars().all())

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
                id=scan.id,
                created_at=scan.created_at,
                predicted_class=(
                    scan.predicted_class.value
                    if hasattr(scan.predicted_class, "value")
                    else scan.predicted_class
                ),
                subtype=scan.subtype,
                confidence=scan.confidence,
                source_node_id=scan.source_node_id,
                confirmed_bin=scan.confirmed_bin,
                image_ref=scan.image_ref,
                latency_ms=scan.latency_ms,
            )
            for scan in scans
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
