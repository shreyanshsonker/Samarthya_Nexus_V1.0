import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class HTTPClient:
    def __init__(self, timeout: int = 2):
        self.timeout = timeout
        
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                logger.error(f"HTTP GET Error on {url}: {exc}")
                raise

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, data=data, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                logger.error(f"HTTP POST Error on {url}: {exc}")
                raise

http_client = HTTPClient()
