# 🤖 AI Telegram Bot

Telegram-бот для доступа к различным AI-моделям через подписочную токеновую систему.

## 📋 Содержание

- [Возможности](#-возможности)
- [Технологический стек](#-технологический-стек)
- [Архитектура](#-архитектура)
- [Установка](#-установка)
- [Конфигурация](#-конфигурация)
- [Запуск](#-запуск)
- [Структура проекта](#-структура-проекта)
- [API Ключи](#-получение-api-ключей)
- [Миграции БД](#-миграции-базы-данных)
- [Разработка](#-разработка)

---

## 🚀 Возможности

### AI Модели

**Текстовые модели:**
- ChatGPT (GPT-4, GPT-4 Mini)
- Claude 3.5 Sonnet (Anthropic)
- Gemini Pro (Google)
- DeepSeek V2
- Sonar (Perplexity)

**Генерация изображений:**
- Nano Banana
- DALL-E 3 (OpenAI)
- Midjourney
- Stable Diffusion
- Recraft
- Замена лиц (Face Swap)

**Генерация видео:**
- Sora 2 (OpenAI)
- Veo 3.1 (Google)
- Midjourney Video
- Hailuo
- Luma
- Kling
- Kling Effects

**Аудио:**
- Suno (создание музыки)
- Whisper (распознавание речи)
- TTS (синтез речи)

**Инструменты для работы с фото:**
- Улучшение качества
- Удаление фона
- Замена фона
- Векторизация

### Система подписок

**Временные подписки:**
- 7 дней — 150,000 токенов — 98 руб.
- 14 дней — 250,000 токенов — 196 руб.
- 21 день — 500,000 токенов — 289 руб.
- 30 дней — 1,000,000 токенов — 597 руб.
- 30 дней — 5,000,000 токенов — 2790 руб.
- Безлимит на 1 день — 199 руб.

**Вечные токены:**
- 150,000 токенов — 149 руб.
- 250,000 токенов — 279 руб.
- 500,000 токенов — 519 руб.
- 1,000,000 токенов — 999 руб.

### Дополнительные функции

- 💬 Диалоги с историей и ролями
- 🤝 Реферальная программа (50% токенов / 10% денег)
- 🔢 Система промокодов
- 📊 Статистика и аналитика
- 🔐 Админ-панель

---

## 🛠 Технологический стек

### Backend
- **Python 3.11+** - основной язык
- **aiogram 3.x** - Telegram Bot Framework
- **FastAPI** - REST API и webhook
- **PostgreSQL 15+** - основная БД
- **SQLAlchemy 2.0** - ORM (async)
- **Alembic** - миграции БД
- **Redis 7+** - кеш и FSM хранилище
- **APScheduler** - фоновые задачи

### AI Integration
- **OpenAI API** - GPT, DALL-E, Whisper, TTS
- **Anthropic API** - Claude
- **Google AI API** - Gemini, Veo
- **Replicate** - различные модели

### Payment
- **ЮKassa API** - платежная система

### DevOps
- **Structlog** - структурированное логирование
- **Pytest** - тестирование
- **Pydantic** - валидация

---

## 🏗 Архитектура

Проект построен на модульной асинхронной архитектуре:

```
┌─────────────────────────────────────────────────┐
│            TELEGRAM USERS                       │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────┐              ┌─────▼──────┐
│  BOT   │              │ ADMIN BOT  │
│(main.py)              │(admin_main) │
└───┬────┘              └─────┬──────┘
    │                         │
    │  ┌──────────────────────┘
    │  │
┌───▼──▼─────────────────────────────┐
│         CORE LAYER                 │
│  - Config  - Logger  - Exceptions  │
│  - Redis   - Scheduler             │
└───────────┬────────────────────────┘
            │
┌───────────▼────────────────────────┐
│      DATABASE LAYER                │
│  - Models  - Repositories          │
│  - PostgreSQL (async)              │
└───────────┬────────────────────────┘
            │
┌───────────▼────────────────────────┐
│      SERVICES LAYER                │
│  - User Service                    │
│  - Subscription Service            │
│  - AI Services (OpenAI, Anthropic) │
│  - Payment Service (YooKassa)      │
│  - File Storage Service            │
└────────────────────────────────────┘
```

**Ключевые принципы:**
- Полная асинхронность (async/await)
- Repository Pattern для БД
- Service Layer для бизнес-логики
- Dependency Injection
- FSM для состояний пользователя
- Middleware для аутентификации и логирования

---

## 📦 Установка

### Требования

- Ubuntu 20.04+ / Debian 11+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- 2GB RAM минимум
- 10GB свободного места

### Автоматическая установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/yourusername/ai-bot-misha.git
cd ai-bot-misha

# 2. Запустите скрипт установки
bash scripts/setup_env.sh
```

Скрипт автоматически:
- Установит PostgreSQL и создаст БД
- Установит Redis
- Создаст виртуальное окружение Python
- Установит все зависимости
- Применит миграции БД
- Создаст необходимые директории

### Ручная установка

<details>
<summary>Показать инструкцию по ручной установке</summary>

#### 1. Установка PostgreSQL

```bash
sudo apt-get update
sudo apt-get install -y postgresql-15
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. Создание базы данных

```bash
sudo -u postgres psql
```

```sql
CREATE USER ai_bot_user WITH PASSWORD 'your_password';
CREATE DATABASE ai_bot OWNER ai_bot_user;
GRANT ALL PRIVILEGES ON DATABASE ai_bot TO ai_bot_user;
\q
```

#### 3. Установка Redis

```bash
sudo apt-get install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### 4. Установка Python зависимостей

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Миграции БД

```bash
cp alembic.ini.example alembic.ini
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

</details>

---

## ⚙️ Конфигурация

### Создание .env файла

```bash
cp .env.example .env
nano .env
```

### Основные параметры

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_BOT_TOKEN=987654321:ZYXwvuTSRqponMLKjiHGfeDCBA
ADMIN_USER_IDS=123456789,987654321

# Database
DATABASE_URL=postgresql+asyncpg://ai_bot_user:your_password@localhost:5432/ai_bot

# Redis
REDIS_URL=redis://localhost:6379/0

# AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...

# Payment
YUKASSA_SHOP_ID=123456
YUKASSA_SECRET_KEY=live_...

# App
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

---

## 🚀 Запуск

### Активация виртуального окружения

```bash
source venv/bin/activate
```

### Запуск основного бота

```bash
python main.py
```

### Запуск админ-бота

```bash
python admin_main.py
```

### Запуск API сервера

```bash
python api_main.py
```

### Запуск всех сервисов (в отдельных терминалах)

```bash
# Терминал 1 - Основной бот
python main.py

# Терминал 2 - Админ-бот
python admin_main.py

# Терминал 3 - API сервер
python api_main.py
```

### Production deployment (с supervisor)

<details>
<summary>Конфигурация Supervisor</summary>

Создайте файл `/etc/supervisor/conf.d/aibot.conf`:

```ini
[program:aibot]
command=/path/to/ai-bot-misha/venv/bin/python main.py
directory=/path/to/ai-bot-misha
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/aibot/main.err.log
stdout_logfile=/var/log/aibot/main.out.log

[program:aibot_admin]
command=/path/to/ai-bot-misha/venv/bin/python admin_main.py
directory=/path/to/ai-bot-misha
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/aibot/admin.err.log
stdout_logfile=/var/log/aibot/admin.out.log

[program:aibot_api]
command=/path/to/ai-bot-misha/venv/bin/python api_main.py
directory=/path/to/ai-bot-misha
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/aibot/api.err.log
stdout_logfile=/var/log/aibot/api.out.log
```

Запуск:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

</details>

---

## 📁 Структура проекта

```
ai-bot-misha/
├── app/
│   ├── core/              # Ядро (конфиг, логирование, redis, scheduler)
│   ├── database/          # Модели БД и репозитории
│   │   ├── models/
│   │   └── repositories/
│   ├── services/          # Бизнес-логика
│   │   ├── ai/           # AI интеграции
│   │   ├── user/
│   │   ├── subscription/
│   │   ├── payment/
│   │   └── ...
│   ├── bot/              # Основной бот
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── middlewares/
│   │   ├── states/
│   │   └── bot_instance.py
│   ├── admin/            # Админ-бот
│   │   └── handlers/
│   ├── api/              # FastAPI приложение
│   │   ├── routes/
│   │   └── webhooks/
│   └── utils/            # Утилиты
├── alembic/              # Миграции БД
├── storage/              # Файловое хранилище
├── scripts/              # Скрипты (setup_env.sh и др.)
├── logs/                 # Логи
├── tests/                # Тесты
├── main.py               # Точка входа основного бота
├── admin_main.py         # Точка входа админ-бота
├── api_main.py           # Точка входа API
├── requirements.txt      # Python зависимости
├── .env.example          # Пример конфигурации
└── README.md             # Документация
```

---

## 🔑 Получение API ключей

### Telegram Bot Token

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

### OpenAI API Key

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Перейдите в [API Keys](https://platform.openai.com/api-keys)
3. Создайте новый ключ
4. Пополните баланс

### Anthropic API Key

1. Зарегистрируйтесь на [console.anthropic.com](https://console.anthropic.com)
2. Создайте API ключ в настройках

### Google AI API Key

1. Перейдите на [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Создайте новый API ключ

### ЮKassa

1. Зарегистрируйтесь на [yookassa.ru](https://yookassa.ru)
2. Пройдите модерацию
3. Получите Shop ID и Secret Key в личном кабинете

---

## 🗄 Миграции базы данных

### Создание новой миграции

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Посмотреть историю
alembic history
```

---

## 👨‍💻 Разработка

### Установка dev-зависимостей

```bash
pip install pytest pytest-asyncio pytest-cov black isort flake8
```

### Запуск тестов

```bash
pytest
pytest --cov=app
```

### Форматирование кода

```bash
black app/
isort app/
```

### Проверка кода

```bash
flake8 app/
```

---

## 📊 Мониторинг

### Логи

Логи сохраняются в директории `logs/`:

```bash
# Просмотр логов основного бота
tail -f logs/bot.log

# Просмотр логов с фильтрацией
tail -f logs/bot.log | grep ERROR
```

### Метрики

Метрики доступны через API:

```bash
curl http://localhost:8000/stats
```

---

## 🔒 Безопасность

- Все API ключи хранятся в `.env` (не коммитится в git)
- Пароли БД должны быть сложными
- Рекомендуется использовать firewall
- Регулярно обновляйте зависимости
- Используйте HTTPS для webhook

---

## 📝 Лицензия

Этот проект создан для образовательных целей.

---

## 🤝 Поддержка

Если возникли вопросы:
- Создайте Issue в GitHub
- Напишите в Telegram: [@support](https://t.me/support)

---

## 🙏 Благодарности

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Web Framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM

---

**Создано с ❤️ для работы с AI моделями**
