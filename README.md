[![Quality&Tests](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml/badge.svg)](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/vol1ura/parkrun_bot/branch/master/graph/badge.svg?token=HFV9PFM5UL)](https://codecov.io/gh/vol1ura/parkrun_bot)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet)](https://www.python.org/dev/peps/pep-0008/) 
![GitHub last commit](https://img.shields.io/github/last-commit/vol1ura/parkrun_bot)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vol1ura/parkrun_bot)

# Telegram Parkrun bot

It is my personal project.

### Configuration

```shell
heroku logs -a <app_name> -d web.1 -n 100
heroku config -a <app_name> | grep REDIS
```

### Tests

```shell
pip install -r tests/requirements.txt
pytest --cov-report=term-missing:skip-covered --cov=. tests/
```