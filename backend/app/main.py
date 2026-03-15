from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.db.influxdb_client import influx_db
from app.db.redis_client import redis_client
from app.services.scheduler import polling_scheduler
from app.services.websocket_manager import websocket_push_loop
from app.routers import auth, energy, carbon, forecast, recommendations, websocket, inverter, data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    await influx_db.connect()
    
    # Start APScheduler for 5min interval polling
    polling_scheduler.start()
    
    # Spawn background 30s WebSocket loop
    push_task = asyncio.create_task(websocket_push_loop())
    
    yield
    
    # Shutdown
    push_task.cancel()
    polling_scheduler.stop()
    await redis_client.close()
    await influx_db.close()

app = FastAPI(
    title="Samarthya Nexus API",
    description="Backend API for Samarthya Nexus - AI-Driven Carbon Footprint Analyzer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(energy.router, prefix="/api/energy", tags=["Energy"])
app.include_router(carbon.router, prefix="/api/carbon", tags=["Carbon"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(inverter.router, prefix="/api/inverter", tags=["Inverter"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(data.router, prefix="/data", tags=["Data"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
