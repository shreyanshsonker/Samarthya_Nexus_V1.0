from fastapi import WebSocket
from typing import List
import logging
import asyncio
from app.services.inverter import get_inverter_service
from app.services.carbon_service import carbon_service
from app.services.data_pipeline import data_pipeline

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending to websocket, removing: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

async def websocket_push_loop():
    """
    Background task pushing live energy/carbon data every 30 seconds
    to all connected websocket clients.
    """
    while True:
        if manager.active_connections:
            try:
                inverter = get_inverter_service()
                raw_reading = await inverter.get_current_reading()
                cleaned = data_pipeline.process_raw_reading(raw_reading)
                
                carbon_metrics = await carbon_service.calculate_shadow_grid(
                    solar_kw=cleaned["solar_kw"],
                    consumption_kw=cleaned["consumption_kw"],
                    net_grid_kw=cleaned["net_grid_kw"]
                )
                
                payload = {
                    "type": "energy_update",
                    "data": {
                        "energy": cleaned,
                        "carbon": carbon_metrics
                    }
                }
                
                await manager.broadcast(payload)
            except Exception as e:
                logger.error(f"Error in websocket push loop: {e}")
                
        await asyncio.sleep(30)
