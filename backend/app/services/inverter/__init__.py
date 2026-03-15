from app.services.inverter.base import BaseInverterService
from app.services.inverter.mock_service import MockService
from app.services.inverter.growatt_service import GrowattService
from app.services.inverter.sma_service import SMAService
from app.config import settings

def get_inverter_service(capacity_kw: float = 3.0) -> BaseInverterService:
    if settings.USE_MOCK:
        return MockService(capacity_kw=capacity_kw)
    
    brand = settings.INVERTER_BRAND.lower()
    if brand == "growatt":
        return GrowattService()
    elif brand == "sma":
        return SMAService()
        
    # Default fallback
    return MockService(capacity_kw=capacity_kw)
