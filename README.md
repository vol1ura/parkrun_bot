[![Quality&Tests](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml/badge.svg)](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/vol1ura/parkrun_bot/branch/master/graph/badge.svg?token=HFV9PFM5UL)](https://codecov.io/gh/vol1ura/parkrun_bot)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet)](https://www.python.org/dev/peps/pep-0008/)
![GitHub last commit](https://img.shields.io/github/last-commit/vol1ura/parkrun_bot)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vol1ura/parkrun_bot)

# Telegram S95 bot

Bot for S95 sport event system.

### Configuration

```shell
sudo -u postgres pg_restore -d s95_dev tmp/backup.tar --no-privileges --no-owner -U postgres
```

### Tests

```shell
pip install -r tests/requirements.txt
pytest --cov-report=term-missing:skip-covered --cov=. tests/
```
