from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import logging
from app.services.websocket_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    # In a real app, we'd extract token from query query params or headers here
    # token = websocket.query_params.get("token")
    # await verify_ws_token(token)
    
    await manager.connect(websocket)
    try:
        while True:
            # We wait for messages but don't strictly require them
            # The background task `websocket_push_loop` will handle outbound pushing
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket)
