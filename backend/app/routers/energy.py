from fastapi import APIRouter, Depends
from app.services.inverter import get_inverter_service
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/current")
async def get_current_reading():
    # Try cache first
    cached = await cache_service.get_json("latest_reading:default_household")
    if cached:
        return cached

    service = get_inverter_service()
    reading = await service.get_current_reading()
    return reading

@router.get("/history")
async def get_daily_history():
    service = get_inverter_service()
    history = await service.get_daily_history()
    return history
