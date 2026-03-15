from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from app.config import settings
import logging

class InfluxDBManager:
    def __init__(self):
        self.url = settings.INFLUXDB_URL
        self.token = settings.INFLUXDB_TOKEN
        self.org = settings.INFLUXDB_ORG
        self.bucket = settings.INFLUXDB_BUCKET
        self.client = None
        self.write_api = None
        self.query_api = None

    async def connect(self):
        try:
            self.client = InfluxDBClientAsync(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api()
            self.query_api = self.client.query_api()
            logging.info("Connected to InfluxDB")
        except Exception as e:
            logging.error(f"Failed to connect to InfluxDB: {e}")

    async def close(self):
        if self.client:
            await self.client.close()
            logging.info("Closed InfluxDB connection")

influx_db = InfluxDBManager()
