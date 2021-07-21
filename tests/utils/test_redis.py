from utils import redis


async def test_redis():
    await redis.set_value('test_key', test='passed')
    value = await redis.get_value('test_key')
    print(value)
    assert value == {'test': 'passed'}
