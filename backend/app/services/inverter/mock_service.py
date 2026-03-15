import math
import random
from datetime import datetime
from typing import Dict, Any
from app.services.inverter.base import BaseInverterService

class MockService(BaseInverterService):
    def __init__(self, capacity_kw: float = 3.0):
        self.capacity_kw = capacity_kw

    def _get_solar_power(self, current_time: datetime) -> float:
        """
        Simulates solar generation using a bell curve centered around 1 PM (13:00)
        """
        hour = current_time.hour + current_time.minute / 60.0
        
        # Solar generation roughly between 6 AM and 6 PM
        if hour < 6.0 or hour > 18.0:
            return 0.0
            
        # Peak at 13:00, width of curve determined by standard deviation (approx 3 hours)
        # standard normal pdf: max at 0 is ~0.3989. We scale it to capacity_kw.
        mean = 13.0
        std_dev = 2.5
        
        base_power = self.capacity_kw * math.exp(-0.5 * ((hour - mean) / std_dev) ** 2)
        
        # Add a bit of natural noise (clouds) up to 10% reduction
        noise_factor = random.uniform(0.9, 1.0)
        return round(base_power * noise_factor, 3)

    def _get_consumption_power(self, current_time: datetime) -> float:
        """
        Simulates household consumption
        Peak in morning (7-9) and evening (18-22)
        """
        hour = current_time.hour
        base_load = 0.3 # 300W fridge etc
        
        if 7 <= hour <= 9:
            active_load = random.uniform(1.0, 2.5) # geyser, microwave
        elif 18 <= hour <= 22:
            active_load = random.uniform(1.5, 3.5) # AC, TV, lighting
        else:
            active_load = random.uniform(0.1, 0.8) # sporadic usage
            
        return round(base_load + active_load, 3)

    async def get_current_reading(self) -> Dict[str, Any]:
        now = datetime.now()
        solar = self._get_solar_power(now)
        consumption = self._get_consumption_power(now)
        
        # Negative net_grid means exporting to grid, positive means importing from grid
        net_grid = round(consumption - solar, 3)
        
        return {
            "timestamp": now.isoformat(),
            "solar_kw": solar,
            "consumption_kw": consumption,
            "net_grid_kw": net_grid,
            "device_status": "mock_running",
            "source": "mock_engine"
        }

    async def get_daily_history(self) -> list[Dict[str, Any]]:
        # For simplicity in mock, just generate 15-min intervals for the current day up to now
        history = []
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        current = start_of_day
        while current <= now:
            solar = self._get_solar_power(current)
            consumption = self._get_consumption_power(current)
            history.append({
                "timestamp": current.isoformat(),
                "solar_kw": solar,
                "consumption_kw": consumption,
                "net_grid_kw": round(consumption - solar, 3),
                "source": "mock_engine"
            })
            # Add 15 mins
            current_minutes = current.minute + 15
            if current_minutes >= 60:
                if current.hour == 23:
                    break
                current = current.replace(hour=current.hour + 1, minute=current_minutes % 60)
            else:
                current = current.replace(minute=current_minutes)
                
        return history
