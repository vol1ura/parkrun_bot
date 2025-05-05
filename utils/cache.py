from aioredis import Redis
from typing import Optional, Any, Union
import json
from app import logger

class Cache:
    def __init__(self, redis: Redis, prefix: str = "cache:"):
        self.redis = redis
        self.prefix = prefix

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(f"{self.prefix}{key}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            await self.redis.setex(
                f"{self.prefix}{key}",
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            await self.redis.delete(f"{self.prefix}{key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear(self, pattern: str = "*") -> bool:
        try:
            keys = await self.redis.keys(f"{self.prefix}{pattern}")
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False 