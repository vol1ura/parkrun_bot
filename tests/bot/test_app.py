import app


def test_app():
    assert app.bot is not None
    assert app.dp is not None
    assert app.logger is not None
