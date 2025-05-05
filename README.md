[![Quality&Tests](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml/badge.svg)](https://github.com/vol1ura/parkrun_bot/actions/workflows/python-app.yml)
[![codecov](https://codecov.io/gh/vol1ura/parkrun_bot/branch/master/graph/badge.svg?token=HFV9PFM5UL)](https://codecov.io/gh/vol1ura/parkrun_bot)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet)](https://www.python.org/dev/peps/pep-0008/)
![GitHub last commit](https://img.shields.io/github/last-commit/vol1ura/parkrun_bot)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/vol1ura/parkrun_bot)

# Parkrun Bot

Телеграм-бот для автоматизации процессов parkrun, включая регистрацию, получение QR-кодов и статистики.

## Возможности

- 🏃‍♂️ Регистрация в системе S95
- 📱 Получение персонального QR-кода
- 📊 Просмотр личной статистики забегов
- 🏆 Установка домашнего забега и клуба
- 📞 Управление контактной информацией
- 🖼 Интеграция с VK для публикации фотографий

## Требования

- Python 3.10+
- PostgreSQL
- Docker (опционально)

## Чувствительные данные

В проекте используются следующие чувствительные данные, которые замаскированы как `--SENSITIVE--`:

1. Токены и ключи:
   - API_BOT_TOKEN
   - INTERNAL_API_KEY
   - ROLLBAR_TOKEN
   - WEBHOOK

2. Данные для подключения:
   - DATABASE_URL
   - REDIS_URL
   - HOST
   - SMTP_SERVER

3. Учетные данные:
   - EMAIL_ADDRESS
   - EMAIL_PASSWORD
   - POSTGRES_USER
   - POSTGRES_PASSWORD

4. Другие конфиденциальные данные:
   - EMAIL_SENDER

## Установка

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd parkrun_bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example` и заполните необходимые переменные окружения:
```bash
cp .env.example .env
```

### Docker установка

1. Соберите образ:
```bash
docker-compose build
```

2. Запустите контейнеры:
```bash
docker-compose up -d
```

## Конфигурация

Основные настройки находятся в файле `config.py`. Для локальной разработки создайте файл `.env` со следующими переменными:

```env
API_BOT_TOKEN=your_telegram_bot_token
VK_SERVICE_TOKEN=your_vk_service_token
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
PRODUCTION_ENV=False
```

## Структура проекта

```
parkrun_bot/
├── app.py              # Основной файл приложения
├── main.py            # Точка входа
├── config.py          # Конфигурация
├── handlers/          # Обработчики команд
├── utils/            # Вспомогательные функции
├── s95/              # Интеграция с S95
├── tests/            # Тесты
└── deploy/           # Файлы для развертывания
```

## Команды бота

- `/start` - Начало работы с ботом
- `/qrcode` - Получить QR-код для S95
- `/register` - Зарегистрироваться в системе
- `/statistics` - Посмотреть личную статистику
- `/help` - Получить справку
- `/phone` - Поделиться номером телефона
- `/club` - Установить клуб
- `/home` - Установить домашний забег
- `/reset` - Отменить текущее действие

## Разработка

### Запуск тестов

```bash
python -m pytest tests/
```

### Линтинг

```bash
make lint
```

### Форматирование кода

```bash
make format
```

## Развертывание

### Используя Docker

1. Настройте переменные окружения в `docker-compose.yml`
2. Запустите:
```bash
docker-compose up -d
```

### На сервере

1. Настройте systemd сервис (пример в `deploy/parkrun_bot.service`)
2. Включите и запустите сервис:
```bash
sudo systemctl enable parkrun_bot
sudo systemctl start parkrun_bot
```

## Мониторинг

- Логи сохраняются в `bot.log`
- В продакшен режиме используется webhook
- Доступна интеграция с системой мониторинга через HTTP эндпоинты

## Тестирование

Проект содержит полный набор тестов:
- Модульные тесты для всех компонентов
- Интеграционные тесты для API
- Тесты для работы с базой данных
- Моки для внешних сервисов (VK, S95)

## Лицензия

MIT

## Поддержка

При возникновении проблем создавайте issue в репозитории проекта.

## Настройка переменных окружения

### Основные настройки
- `PRODUCTION` - режим работы (true/false)
- `VERSION` - версия бота

### Настройки бота
- `API_BOT_TOKEN` - токен Telegram бота
- `WEBHOOK` - путь для webhook
- `HOST` - хост для webhook
- `PORT` - порт для webhook

### Настройки базы данных
- `DATABASE_URL` - URL подключения к PostgreSQL
- `DB_MIN_SIZE` - минимальный размер пула соединений
- `DB_MAX_SIZE` - максимальный размер пула соединений
- `DB_COMMAND_TIMEOUT` - таймаут выполнения команд (сек)
- `DB_MAX_QUERIES` - максимальное количество запросов
- `DB_MAX_INACTIVE_TIME` - максимальное время неактивности соединения (сек)

### Настройки Redis
- `REDIS_URL` - URL подключения к Redis
- `REDIS_ENCODING` - кодировка
- `REDIS_DECODE_RESPONSES` - декодирование ответов

### Настройки rate limiting
- `RATE_LIMIT` - лимит запросов
- `RATE_WINDOW` - временное окно (сек)

### Настройки кэширования
- `CACHE_TTL` - время жизни кэша (сек)
- `CACHE_PREFIX` - префикс для ключей кэша

### Настройки API
- `INTERNAL_API_KEY` - ключ для внутреннего API
- `INTERNAL_API_URL` - URL внутреннего API
- `API_TIMEOUT` - таймаут для API запросов (сек)

### Настройки мониторинга
- `ROLLBAR_TOKEN` - токен для Rollbar
- `LOG_LEVEL` - уровень логирования
- `LOG_FILE` - файл для логов

### Настройки email
- `EMAIL_SENDER` - имя отправителя
- `EMAIL_ADDRESS` - email адрес
- `EMAIL_PASSWORD` - пароль от email
- `SMTP_PORT` - порт SMTP сервера
- `SMTP_SERVER` - адрес SMTP сервера

## Запуск

1. Запустите бота:
```bash
python main.py
```

2. Для разработки:
```bash
python main.py --dev
```

## Тестирование

```bash
pytest
```

## Оптимизации

Бот включает следующие оптимизации:
- Кэширование с использованием Redis
- Rate limiting для защиты от перегрузки
- Пул соединений с базой данных
- Асинхронная обработка запросов
- Мониторинг и логирование
- Обработка ошибок и повторные попытки

## Development

### Configuration

```shell
sudo -u postgres pg_restore -d s95_dev deploy/backup.tar --no-privileges --no-owner -U postgres
```

### Tests

```shell
pip install -r tests/requirements.txt
pytest --cov-report=term-missing:skip-covered --cov=. tests/
```

For html report:
```shell
pytest --cov-report=html --cov=. tests/
```
