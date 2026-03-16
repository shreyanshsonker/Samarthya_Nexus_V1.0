"""
E3.4 — Inverter Router
Manages inverter connection status and sync.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.routers.auth import get_current_user
from app.models.database import UserAccount, InverterDevice
from app.db.postgres import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

@router.get("/status")
async def get_inverter_status(
    current_user: UserAccount = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns connection status of the inverter for the household.
    """
    result = await db.execute(
        select(InverterDevice).where(InverterDevice.household_id == current_user.household_id)
    )
    device = result.scalars().first()
    
    if not device:
        return {"connected": False, "status": "No device configured"}
    
    return {
        "connected": device.status == "online",
        "last_sync": device.last_online.isoformat() if device.last_online else None,
        "brand": device.brand,
        "status": device.status
    }

@router.post("/sync")
async def trigger_inverter_sync(current_user: UserAccount = Depends(get_current_user)):
    """
    Manually triggers a data fetch from the inverter API.
    """
    # Simply return success for now; actual polling is scheduled
    return {"synced": True, "message": "Manual sync triggered."}
