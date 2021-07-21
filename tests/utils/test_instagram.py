import os
import pytest
from utils.instagram import get_last_post


@pytest.mark.xfail
def test_get_last_post():
    username = os.environ.get('IG_USERNAME')
    password = os.environ.get('IG_PASSWORD')
    post_url, post = get_last_post(username, password, 'rocketscienze')
    assert isinstance(post, str)
    assert isinstance(post_url, str)
    assert post_url.startswith('https://')
    assert 1 <= len(post.split('\n\n')) <= 2
