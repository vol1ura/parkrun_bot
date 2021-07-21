import aioredis
from config import REDIS_URL


async def get_value(key: str):
    db = await aioredis.create_redis_pool(REDIS_URL)
    value = await db.hgetall(key, encoding='utf-8')
    db.close()
    await db.wait_closed()
    return value


async def set_value(key, **kwargs):
    db = await aioredis.create_redis_pool(REDIS_URL)
    await db.hmset_dict(key, **kwargs)
    db.close()
    await db.wait_closed()
