from asyncpg import Pool, create_pool
from typing import Optional, Dict, Any, List
import logging
from functools import wraps
import asyncio
from .cache import Cache

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20, cache: Optional[Cache] = None):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[Pool] = None
        self.cache = cache

    async def connect(self):
        try:
            self.pool = await create_pool(
                self.dsn,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=60,
                max_queries=50000,
                max_inactive_connection_lifetime=300
            )
            logger.info("Database pool created successfully")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

    async def execute(self, query: str, *args) -> Optional[Dict[str, Any]]:
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except Exception as e:
            logger.error(f"Database execute error: {e}")
            return None

    async def execute_many(self, query: str, *args) -> List[Dict[str, Any]]:
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except Exception as e:
            logger.error(f"Database execute_many error: {e}")
            return []

    def with_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                _tries, _delay = max_retries, delay
                while _tries > 0:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        _tries -= 1
                        if _tries == 0:
                            logger.error(f"Max retries exceeded: {e}")
                            raise
                        logger.warning(f"Retrying {func.__name__} after error: {e}")
                        await asyncio.sleep(_delay)
                        _delay *= backoff
            return wrapper
        return decorator

    @with_retry()
    async def find_user_by(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        if self.cache:
            cache_key = f"user:{field}:{value}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        query = f"SELECT * FROM users WHERE {field} = $1"
        result = await self.execute(query, value)

        if self.cache and result:
            await self.cache.set(cache_key, result, ttl=300)

        return result

    @with_retry()
    async def find_athlete_by(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        if self.cache:
            cache_key = f"athlete:{field}:{value}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        query = f"SELECT * FROM athletes WHERE {field} = $1"
        result = await self.execute(query, value)

        if self.cache and result:
            await self.cache.set(cache_key, result, ttl=300)

        return result

    @with_retry()
    async def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        try:
            fields = ', '.join(f"{k} = ${i+2}" for i, k in enumerate(data.keys()))
            query = f"UPDATE users SET {fields} WHERE id = $1"
            
            async with self.pool.acquire() as conn:
                await conn.execute(query, user_id, *data.values())
                
                if self.cache:
                    # Очищаем кэш для этого пользователя
                    await self.cache.clear(f"user:*:{user_id}")
                
                return True
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return False 