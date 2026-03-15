import json
import logging
from typing import Optional, Any, Dict
from app.db.redis_client import redis_client

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl # Default 1 hour

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stores a JSON-serializable value in Redis.
        """
        try:
            if not redis_client.client:
                return False
            
            payload = json.dumps(value)
            expire = ttl if ttl is not None else self.ttl
            await redis_client.client.set(key, payload, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis set_json failed for key {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Retrieves a JSON-serializable value from Redis.
        """
        try:
            if not redis_client.client:
                return None
            
            data = await redis_client.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get_json failed for key {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Deletes a key from Redis.
        """
        try:
            if not redis_client.client:
                return False
            await redis_client.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return False

    async def cache_latest_reading(self, household_id: str, reading: Dict[str, Any]):
        """
        Specialized helper to cache the latest inverter reading for a household.
        """
        key = f"latest_reading:{household_id}"
        await self.set_json(key, reading, ttl=300) # 5 min cache for "latest"

cache_service = CacheService()
