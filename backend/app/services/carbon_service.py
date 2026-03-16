from app.utils.constants import GRID_INTENSITY_MP_FALLBACK, TREE_DAILY_ABSORPTION
from app.utils.http_client import http_client
from app.config import settings
from app.db.influxdb_client import influx_db
from typing import Dict, Any, List
import logging
from datetime import datetime, timezone, timedelta

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

    async def get_daily_summary(self, household_id: str) -> Dict[str, Any]:
        """
        Aggregate energy and carbon for the last 24 hours.
        """
        query = f'''
        from(bucket: "{influx_db.bucket}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "energy_readings")
          |> filter(fn: (r) => r["household_id"] == "{household_id}")
          |> aggregateWindow(every: 24h, fn: sum, createEmpty: false)
        '''
        
        # Note: In a real system, we'd use flux to calculate kWh (sum * 0.25).
        # For simplicity in this MVP logic:
        try:
            tables = await influx_db.query_api.query(query)
            data = {"solar_kwh": 0.0, "consumption_kwh": 0.0, "saved_kg": 0.0}
            
            for table in tables:
                for record in table.records:
                    field = record.get_field()
                    val = record.get_value() * 0.25 # 15-min to kWh
                    if field == "solar_kw":
                        data["solar_kwh"] = round(val, 2)
                    elif field == "consumption_kw":
                        data["consumption_kwh"] = round(val, 2)
            
            data["saved_kg"] = round(data["solar_kwh"] * self.fallback_intensity, 2)
            data["trees"] = round(data["saved_kg"] / self.tree_absorption, 2)
            return data
        except Exception as e:
            logger.error(f"Daily summary query failed: {e}")
            return {"solar_kwh": 0.0, "consumption_kwh": 0.0, "saved_kg": 0.0, "trees": 0.0}

    async def get_weekly_summary(self, household_id: str) -> List[Dict[str, Any]]:
        """
        Aggregate energy and carbon for the last 7 days.
        """
        query = f'''
        from(bucket: "{influx_db.bucket}")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "energy_readings")
          |> filter(fn: (r) => r["household_id"] == "{household_id}")
          |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
        '''
        
        try:
            tables = await influx_db.query_api.query(query)
            # Organise by date
            records_by_day = {}
            for table in tables:
                for record in table.records:
                    date_str = record.get_time().date().isoformat()
                    if date_str not in records_by_day:
                        records_by_day[date_str] = {"date": date_str, "solar_kwh": 0.0, "saved_kg": 0.0}
                    
                    field = record.get_field()
                    val = record.get_value() * 0.25
                    if field == "solar_kw":
                        records_by_day[date_str]["solar_kwh"] = round(val, 2)
                        records_by_day[date_str]["saved_kg"] = round(val * self.fallback_intensity, 2)
            
            return sorted(records_by_day.values(), key=lambda x: x["date"])
        except Exception as e:
            logger.error(f"Weekly summary query failed: {e}")
            return []

carbon_service = CarbonService()

