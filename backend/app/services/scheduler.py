import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.inverter import get_inverter_service
from app.services.data_pipeline import data_pipeline
from app.db.influxdb_client import influx_db
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

class PollingScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    async def poll_inverter_data(self):
        """
        Triggered every 5 minutes by the scheduler.
        """
        try:
            logger.info("Polling Inverter API for new data...")
            inverter = get_inverter_service()
            raw_reading = await inverter.get_current_reading()
            
            # Clean and normalize
            cleaned_reading = data_pipeline.process_raw_reading(raw_reading)
            
            # Cache latest for sub-10ms UI retrieval
            await cache_service.cache_latest_reading("default_household", cleaned_reading)
            
            # Push to InfluxDB Async
            if influx_db.write_api:
                # Based on Epic 4: InfluxDB schema
                point = {
                    "measurement": "energy_readings",
                    "tags": {"source": cleaned_reading.get("source", "unknown")},
                    "fields": {
                        "solar_kw": float(cleaned_reading["solar_kw"]),
                        "consumption_kw": float(cleaned_reading["consumption_kw"]),
                        "net_grid_kw": float(cleaned_reading["net_grid_kw"])
                    },
                    "time": cleaned_reading["timestamp"]
                }
                
                # We offload the write to not block the scheduler loop
                # In python influxdb-client-async, write is async
                await influx_db.write_api.write(bucket=influx_db.bucket, record=point)
                logger.info(f"Successfully recorded data point: {cleaned_reading['timestamp']}")
            else:
                logger.warning("InfluxDB write_api not initialized; skipping data point.")
                
        except Exception as e:
            logger.error(f"Error during inverter polling task: {e}")

    def start(self):
        # Poll every 5 minutes
        self.scheduler.add_job(
            self.poll_inverter_data, 
            'interval', 
            minutes=5, 
            id='inverter_poll'
        )
        self.scheduler.start()
        logger.info("Polling Scheduler started.")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Polling Scheduler stopped.")

polling_scheduler = PollingScheduler()
