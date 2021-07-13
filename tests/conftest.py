import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope='session', autouse=True)
def test_dot_env_mock():
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)


pytest_plugins = 'aiohttp.pytest_plugin'
