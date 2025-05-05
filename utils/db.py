import asyncpg
from app import logger
from functools import wraps
import json
from typing import Optional, Dict, Any

# Кэш для часто используемых данных
cache = {}

def cache_result(ttl: int = 300):  # 5 минут по умолчанию
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаем ключ кэша из аргументов функции
            cache_key = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            
            # Проверяем кэш
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return cached_data
            
            # Если нет в кэше или устарел, выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем результат в кэш
            cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

async def execute_query(pool: asyncpg.Pool, query: str, *args) -> Optional[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return None

@cache_result(ttl=300)
async def find_user_by(pool: asyncpg.Pool, field: str, value: Any) -> Optional[Dict[str, Any]]:
    query = f"SELECT * FROM users WHERE {field} = $1"
    return await execute_query(pool, query, value)

@cache_result(ttl=300)
async def find_athlete_by(pool: asyncpg.Pool, field: str, value: Any) -> Optional[Dict[str, Any]]:
    query = f"SELECT * FROM athletes WHERE {field} = $1"
    return await execute_query(pool, query, value)

async def update_user(pool: asyncpg.Pool, user_id: int, data: Dict[str, Any]) -> bool:
    try:
        async with pool.acquire() as conn:
            fields = ', '.join(f"{k} = ${i+2}" for i, k in enumerate(data.keys()))
            query = f"UPDATE users SET {fields} WHERE id = $1"
            await conn.execute(query, user_id, *data.values())
            return True
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return False

async def create_user(pool: asyncpg.Pool, data: Dict[str, Any]) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            fields = ', '.join(data.keys())
            values = ', '.join(f"${i+1}" for i in range(len(data)))
            query = f"INSERT INTO users ({fields}) VALUES ({values}) RETURNING id"
            return await conn.fetchval(query, *data.values())
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None 