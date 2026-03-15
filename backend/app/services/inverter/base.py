from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseInverterService(ABC):
    @abstractmethod
    async def get_current_reading(self) -> Dict[str, Any]:
        """
        Returns a dictionary containing at minimum:
        - solar_kw
        - consumption_kw
        - net_grid_kw
        - device_status
        """
        pass

    @abstractmethod
    async def get_daily_history(self) -> list[Dict[str, Any]]:
        """
        Returns historical readings for the day.
        """
        pass
