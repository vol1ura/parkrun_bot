import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope='session', autouse=True)
def setup_dot_env():
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path)


pytest_plugins = 'aiohttp.pytest_plugin'
