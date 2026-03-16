from fastapi import APIRouter, Depends
from app.services.inverter import get_inverter_service
from app.services.cache_service import cache_service
from app.routers.auth import get_current_user
from app.models.database import UserAccount

router = APIRouter()

@router.get("/current")
async def get_current_reading(current_user: UserAccount = Depends(get_current_user)):
    # Try cache first
    household_id = str(current_user.household_id)
    cache_key = f"latest_reading:{household_id}"
    
    cached = await cache_service.get_json(cache_key)
    if cached:
        return cached

    service = get_inverter_service()
    reading = await service.get_current_reading()
    return reading

@router.get("/history")
async def get_daily_history(current_user: UserAccount = Depends(get_current_user)):
    # This might need to query InfluxDB for actual history
    service = get_inverter_service()
    history = await service.get_daily_history()
    return history
