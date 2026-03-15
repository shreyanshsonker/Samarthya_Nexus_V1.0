from datetime import datetime
from typing import Dict, Any
import logging
from app.services.inverter.base import BaseInverterService
from app.utils.http_client import http_client
from app.config import settings

logger = logging.getLogger(__name__)

class GrowattService(BaseInverterService):
    def __init__(self):
        self.username = settings.GROWATT_USER
        self.password = settings.GROWATT_PASS
        # MOCK IMPLEMENTATION URI: Instead of real API, simulating
        self.base_url = "https://mock.samarthya.app/growatt"
        
    async def get_current_reading(self) -> Dict[str, Any]:
        """
        Simulates fetching from ShinePhone API using http_client.
        In reality, we mock the response to avoid hitting a dead endpoint.
        """
        try:
            # Simulated HTTP Call
            # response = await http_client.post(f"{self.base_url}/login", data={"user": self.username, "password": self.password})
            
            # Simulated return mimicking PRD schema
            now = datetime.now()
            return {
                "timestamp": now.isoformat(),
                "solar_kw": 1.25,
                "consumption_kw": 2.15,
                "net_grid_kw": 0.90, # Importing 900W
                "device_status": "online",
                "source": "growatt_api"
            }
        except Exception as e:
            logger.error(f"Growatt API Error: {e}")
            raise

    async def get_daily_history(self) -> list[Dict[str, Any]]:
        # Simulated sequence
        history = []
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0)
        curr = start
        while curr <= now:
            history.append({
                "timestamp": curr.isoformat(),
                "solar_kw": 1.0, 
                "consumption_kw": 1.5,
                "net_grid_kw": 0.5,
                "source": "growatt_api"
            })
            curr_minutes = curr.minute + 15
            if curr_minutes >= 60:
                if curr.hour == 23: break
                curr = curr.replace(hour=curr.hour + 1, minute=curr_minutes % 60)
            else:
                curr = curr.replace(minute=curr_minutes)
        return history
