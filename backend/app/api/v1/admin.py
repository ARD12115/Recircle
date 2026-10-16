"""
Admin Endpoints - POST /admin/demo/reset, /admin/demo/traffic
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_admin_user
from app.db.session import get_db
from app.services.twin.events import reset_demo_data
from app.services.twin.generator import demo_generator

router = APIRouter()


@router.post("/demo/reset")
async def admin_demo_reset(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo mode disabled")
    """Reset demo data to initial state."""
    await reset_demo_data(db)
    # Also reset generator
    await demo_generator.stop()
    await demo_generator.start(db)
    return {"message": "Demo data reset and traffic generator restarted"}


@router.post("/demo/traffic")
async def admin_demo_traffic(
    start: bool = True,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo mode disabled")
    """Start or stop demo traffic generator."""
    if start:
        await demo_generator.start(db)
        return {"message": "Demo traffic generator started"}
    else:
        await demo_generator.stop()
        return {"message": "Demo traffic generator stopped"}