import redis.asyncio as aioredis
from app.config import settings
import logging

class RedisManager:
    def __init__(self):
        self.url = settings.REDIS_URL
        self.redis = None

    async def connect(self):
        try:
            self.redis = aioredis.from_url(self.url, decode_responses=True)
            logging.info("Connected to Redis")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")

    async def close(self):
        if self.redis:
            await self.redis.close()
            logging.info("Closed Redis connection")

redis_client = RedisManager()
