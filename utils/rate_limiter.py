from aioredis import Redis
import time
from app import logger
from typing import Optional

class RateLimiter:
    def __init__(self, redis: Redis, limit: int, window: int):
        self.redis = redis
        self.limit = limit
        self.window = window

    async def is_allowed(self, key: str) -> bool:
        try:
            now = time.time()
            pipeline = self.redis.pipeline()
            
            # Удаляем старые записи
            pipeline.zremrangebyscore(key, 0, now - self.window)
            
            # Получаем количество запросов
            pipeline.zcard(key)
            
            # Добавляем новый запрос
            pipeline.zadd(key, {str(now): now})
            
            # Устанавливаем время жизни ключа
            pipeline.expire(key, self.window)
            
            # Выполняем все команды
            _, count, _, _ = await pipeline.execute()
            
            return count <= self.limit
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return True  # В случае ошибки разрешаем запрос

    async def get_remaining(self, key: str) -> Optional[int]:
        try:
            now = time.time()
            pipeline = self.redis.pipeline()
            
            # Удаляем старые записи
            pipeline.zremrangebyscore(key, 0, now - self.window)
            
            # Получаем количество запросов
            pipeline.zcard(key)
            
            # Выполняем команды
            _, count = await pipeline.execute()
            
            return max(0, self.limit - count)
        except Exception as e:
            logger.error(f"Rate limiter get_remaining error: {e}")
            return None 