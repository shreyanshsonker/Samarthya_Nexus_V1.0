from datetime import datetime
from typing import Dict, Any
import logging
from app.services.inverter.base import BaseInverterService
from app.utils.http_client import http_client
from app.config import settings

logger = logging.getLogger(__name__)

class SMAService(BaseInverterService):
    def __init__(self):
        self.client_id = settings.SMA_CLIENT_ID
        self.secret = settings.SMA_SECRET
        self.base_url = "https://mock.samarthya.app/sma"
        
    async def get_current_reading(self) -> Dict[str, Any]:
        """
        Simulates fetching from Sunny Portal API via OAuth2
        """
        try:
            now = datetime.now()
            return {
                "timestamp": now.isoformat(),
                "solar_kw": 2.10,
                "consumption_kw": 1.80,
                "net_grid_kw": -0.30, # Exporting 300W
                "device_status": "ok",
                "source": "sma_api"
            }
        except Exception as e:
            logger.error(f"SMA API Error: {e}")
            raise

    async def get_daily_history(self) -> list[Dict[str, Any]]:
        history = []
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0)
        curr = start
        while curr <= now:
            history.append({
                "timestamp": curr.isoformat(),
                "solar_kw": 1.5, 
                "consumption_kw": 1.0,
                "net_grid_kw": -0.5,
                "source": "sma_api"
            })
            curr_minutes = curr.minute + 15
            if curr_minutes >= 60:
                if curr.hour == 23: break
                curr = curr.replace(hour=curr.hour + 1, minute=curr_minutes % 60)
            else:
                curr = curr.replace(minute=curr_minutes)
        return history
