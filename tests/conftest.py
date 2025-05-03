import os
import pytest
import asyncpg

from dotenv import load_dotenv

import config


@pytest.fixture(scope='session', autouse=True)
def setup_dot_env() -> None:
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path)


@pytest.fixture(name='db_pool', scope='function')
async def setup_db_pool(loop):
    """Create and return a database connection pool for tests"""
    pool = await asyncpg.create_pool(config.DATABASE_URL)
    if pool is None:
        raise Exception('Database connection pool is not created')
    yield pool
    await pool.close()


@pytest.fixture(name='database', scope='function')
async def setup_db(db_pool) -> None:
    """Set up test database tables"""
    async with db_pool.acquire() as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS users (id bigint, name varchar(255), telegram_id bigint)')


pytest_plugins = 'aiohttp.pytest_plugin'
