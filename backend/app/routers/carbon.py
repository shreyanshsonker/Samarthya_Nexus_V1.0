from fastapi import APIRouter, Depends
from app.services.inverter import get_inverter_service
from app.services.carbon_service import carbon_service
from app.routers.auth import get_current_user
from app.models.database import UserAccount

router = APIRouter()

@router.get("/live")
async def get_live_carbon(current_user: UserAccount = Depends(get_current_user)):
    inverter = get_inverter_service()
    energy_reading = await inverter.get_current_reading()
    
    carbon_metrics = await carbon_service.calculate_shadow_grid(
        solar_kw=energy_reading["solar_kw"],
        consumption_kw=energy_reading["consumption_kw"],
        net_grid_kw=energy_reading["net_grid_kw"],
    )
    
    return {
        "energy": energy_reading,
        "carbon": carbon_metrics
    }

@router.get("/daily-summary")
async def get_daily_summary(current_user: UserAccount = Depends(get_current_user)):
    return await carbon_service.get_daily_summary(str(current_user.household_id))

@router.get("/weekly-summary")
async def get_weekly_summary(current_user: UserAccount = Depends(get_current_user)):
    return await carbon_service.get_weekly_summary(str(current_user.household_id))

