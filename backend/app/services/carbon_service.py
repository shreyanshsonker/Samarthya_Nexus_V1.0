from app.utils.constants import GRID_INTENSITY_MP_FALLBACK, TREE_DAILY_ABSORPTION
from app.utils.http_client import http_client
from app.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CarbonService:
    def __init__(self, fallback_intensity: float = GRID_INTENSITY_MP_FALLBACK):
        self.fallback_intensity = fallback_intensity
        self.tree_absorption = TREE_DAILY_ABSORPTION
        
    async def get_current_grid_intensity(self) -> float:
        """
        Fetches live grid carbon intensity. For Gwalior: 26.2, 78.1
        Mocks response for now if not active.
        """
        if not settings.ELECTRICITY_MAPS_TOKEN:
            return self.fallback_intensity
            
        try:
            # We will use a mock URL for development to bypass rate limits
            url = "https://mock.samarthya.app/electricity-maps"
            params = {
                "lat": "26.2",
                "lon": "78.1"
            }
            headers = {"auth-token": settings.ELECTRICITY_MAPS_TOKEN}
            
            # response = await http_client.get(url, params=params, headers=headers)
            # return response.get("carbonIntensity", self.fallback_intensity) / 1000.0 # Convert g/kWh to kg/kWh
            
            # For staging without a real mock server listening:
            return self.fallback_intensity
        except Exception as e:
            logger.warning(f"Electricity Maps API failed, using fallback: {e}")
            return self.fallback_intensity

    async def calculate_shadow_grid(self, solar_kw: float, consumption_kw: float, net_grid_kw: float) -> Dict[str, Any]:
        """
        Calculates carbon metrics based on PRD §6.3 rules.
        """
        grid_pull = max(0.0, net_grid_kw)
        intensity = await self.get_current_grid_intensity()
        
        green_co2 = round(grid_pull * intensity, 3)
        shadow_co2 = round(consumption_kw * intensity, 3)
        offset = round(shadow_co2 - green_co2, 3)
        trees = round(offset / self.tree_absorption, 2)
        
        return {
            "green_co2_kg": green_co2,
            "shadow_co2_kg": shadow_co2,
            "offset_co2_kg": offset,
            "trees_equiv": trees,
            "grid_intensity": intensity
        }

carbon_service = CarbonService()

