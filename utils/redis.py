from app import redis_connection


async def get_value(key):
    return await redis_connection.hgetall(str(key), encoding='utf-8')


async def set_value(key, mapping):
    await redis_connection.hmset(str(key), mapping)
