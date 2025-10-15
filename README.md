[![Quality&Tests](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml/badge.svg)](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/vol1ura/parkrun_bot/branch/master/graph/badge.svg?token=HFV9PFM5UL)](https://codecov.io/gh/vol1ura/parkrun_bot)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet)](https://www.python.org/dev/peps/pep-0008/)
![GitHub last commit](https://img.shields.io/github/last-commit/vol1ura/parkrun_bot)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vol1ura/parkrun_bot)

# Telegram S95 bot

Bot for S95 sport event system.

## Features

- 🤖 Telegram bot integration with aiogram 3.x
- 🔄 Two operation modes: **Polling** (development) and **Webhook** (production)
- 🗄️ PostgreSQL database support with asyncpg
- 🔐 Secure webhook implementation with nginx reverse proxy
- 📊 Statistics and personal data tracking
- 🌍 Multi-language support (Russian, English, Belarusian, Serbian)
- 🎯 QR code generation for S95 system

## Quick Start

### Development Mode (Polling)

1. Install dependencies:
```shell
pip install -r requirements.txt
```

2. Create `.env` file:
```shell
API_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@localhost:5432/s95_dev
```

3. Run the bot:
```shell
python main.py
```

## Development

### Database Configuration

```shell
sudo -u postgres pg_restore -d s95_dev deploy/backup.tar --no-privileges --no-owner -U postgres
```

### Testing

```shell
pip install -r tests/requirements.txt
pytest --cov-report=term-missing:skip-covered --cov=. tests/
```

For html report:
```shell
pytest --cov-report=html --cov=. tests/
```

## Webhook Status Check

Use the included script to verify webhook configuration:

```shell
cd deploy
./check_webhook.sh [bot_token]
```

Or let it read token from `.env` file automatically.

## Architecture

```
┌─────────────┐       ┌──────────┐       ┌─────────┐
│  Telegram   │──────▶│  Nginx   │──────▶│   Bot   │
│     API     │◀──────│  (443)   │◀──────│  (5000) │
└─────────────┘       └──────────┘       └─────────┘
                                               │
                                               ▼
                                          ┌──────────┐
                                          │PostgreSQL│
                                          └──────────┘
```

## Technologies

- **[aiogram 3.x](https://github.com/aiogram/aiogram)** - Telegram Bot framework
- **[asyncpg](https://github.com/MagicStack/asyncpg)** - PostgreSQL async driver
- **PostgreSQL** - Database
- **Nginx** - Reverse proxy for webhook

## Troubleshooting

### Production deployment issues

If bot crashes in production mode:

```bash
# Run diagnostic script
./deploy/diagnose_production.sh
```

**Quick fix:**
1. Edit `.env` file
2. Uncomment `PRODUCTION=1` (or `true`)
3. Ensure `HOST=https://yourdomain.com` (with protocol!)
4. Restart bot: `sudo systemctl restart s95-bot`

Check webhook status:
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

View bot logs:
```bash
sudo journalctl -u s95-bot -f
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

All rights reserved.
