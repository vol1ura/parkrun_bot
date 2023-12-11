import os
import pytest

from dotenv import load_dotenv

from app import db_conn


@pytest.fixture(scope='session', autouse=True)
def setup_dot_env() -> None:
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path)


@pytest.fixture(name='database')
async def setup_db(loop) -> None:
    conn = await db_conn()
    await conn.execute('CREATE TABLE IF NOT EXISTS users (id bigint, name varchar(255), telegram_id bigint)')


pytest_plugins = 'aiohttp.pytest_plugin'
