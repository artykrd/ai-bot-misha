# Инструкция по тестированию исправлений

## Что было исправлено

### 1. Проблема с инициализацией Dispatcher

**Ошибка**: `property 'storage' of 'Dispatcher' object has no setter`

**Причина**: В aiogram 3.x нельзя переназначить storage после создания Dispatcher. Ранее Dispatcher создавался на уровне модуля до подключения к Redis.

**Решение**: Dispatcher теперь создается после подключения к Redis внутри функции setup.

### 2. Измененные файлы

- `app/bot/bot_instance.py` - setup_bot() теперь возвращает Dispatcher
- `main.py` - получает dispatcher из setup_bot() и использует его
- `admin_main.py` - создает dispatcher после подключения к Redis

## Предварительные требования

Перед тестированием убедитесь что:

1. **PostgreSQL запущен и настроен**:
   ```bash
   # Проверка статуса
   systemctl status postgresql

   # Если не запущен
   systemctl start postgresql
   ```

2. **Redis запущен**:
   ```bash
   # Проверка статуса
   systemctl status redis-server

   # Если не запущен
   systemctl start redis-server
   ```

3. **База данных создана**:
   ```bash
   sudo -u postgres psql -c "CREATE DATABASE ai_bot;"
   ```

4. **Пользователь базы данных создан**:
   ```bash
   sudo -u postgres psql -c "CREATE USER ai_bot_user WITH PASSWORD 'your_password_here';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_bot TO ai_bot_user;"
   ```

5. **Python зависимости установлены**:
   ```bash
   pip install -r requirements.txt
   ```

   **Примечание**: Если `yookassa` не установится, это не критично для базового тестирования бота.

6. **Файл .env настроен**:
   ```bash
   # Проверьте что в .env есть все необходимые переменные:
   cat .env | grep -E "TELEGRAM_BOT_TOKEN|DATABASE_URL|REDIS_URL"
   ```

## Пошаговое тестирование

### Шаг 1: Проверка синтаксиса

```bash
python -m py_compile main.py
python -m py_compile admin_main.py
python -m py_compile app/bot/bot_instance.py
```

Если нет ошибок - синтаксис корректен.

### Шаг 2: Запуск миграций базы данных

```bash
alembic upgrade head
```

Ожидаемый результат:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, initial
```

### Шаг 3: Тестирование основного бота

```bash
python main.py
```

**Ожидаемые логи** (без ошибок):
```
{"event": "bot_starting", "environment": "development", ...}
{"event": "database_connection_established", ...}
{"event": "redis_connected", ...}
{"event": "bot_setup_completed", ...}
{"event": "bot_started_successfully", ...}
```

**Что проверить**:
- ✅ Бот запустился без ошибок
- ✅ Подключение к Redis успешно
- ✅ Подключение к базе данных успешно
- ✅ Dispatcher создан с Redis storage
- ✅ Все хендлеры и middleware зарегистрированы

### Шаг 4: Тестирование в Telegram

1. Откройте бота в Telegram
2. Отправьте команду `/start`
3. Проверьте что:
   - ✅ Бот отвечает
   - ✅ Отображается главное меню
   - ✅ Показывается баланс токенов
   - ✅ Пользователь создан в базе данных

### Шаг 5: Тестирование админ-бота (опционально)

```bash
# Остановите основной бот (Ctrl+C) и запустите админ-бот
python admin_main.py
```

**Ожидаемые логи**:
```
{"event": "admin_bot_starting", ...}
{"event": "admin_bot_started", ...}
```

Отправьте `/start` админскому боту и проверьте админ-панель.

### Шаг 6: Проверка корректного завершения

Нажмите `Ctrl+C` для остановки бота.

**Ожидаемые логи при остановке**:
```
{"event": "bot_shutting_down", ...}
{"event": "redis_disconnected", ...}
{"event": "database_connection_closed", ...}
{"event": "bot_shutdown_complete", ...}
```

## Возможные проблемы и решения

### 1. ModuleNotFoundError: No module named 'aiogram'

**Решение**: Установите зависимости:
```bash
pip install -r requirements.txt
```

### 2. Redis connection refused

**Решение**: Запустите Redis:
```bash
systemctl start redis-server
# или
redis-server --daemonize yes
```

### 3. Database connection failed

**Решение**: Проверьте DATABASE_URL в .env и убедитесь что:
- PostgreSQL запущен
- База данных создана
- Пользователь создан с правильным паролем

### 4. password authentication failed

**Решение**: Пересоздайте пользователя с паролем из .env:
```bash
sudo -u postgres psql -c "DROP USER IF EXISTS ai_bot_user;"
sudo -u postgres psql -c "CREATE USER ai_bot_user WITH PASSWORD 'ваш_пароль_из_env';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_bot TO ai_bot_user;"
```

### 5. Telegram bot token invalid

**Решение**: Получите новый токен от @BotFather и обновите TELEGRAM_BOT_TOKEN в .env

## Тестирование юнит-тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app tests/

# Запуск конкретного теста
pytest tests/test_config.py -v
```

## Checklist успешного тестирования

- [ ] Python зависимости установлены
- [ ] PostgreSQL запущен и доступен
- [ ] Redis запущен и доступен
- [ ] База данных создана
- [ ] Миграции применены успешно
- [ ] Основной бот запускается без ошибок
- [ ] Бот отвечает на команду /start в Telegram
- [ ] Пользователь создается в базе данных
- [ ] Бот корректно завершается (Ctrl+C)
- [ ] Админ-бот запускается (опционально)

## Следующие шаги

После успешного тестирования:

1. **Создайте коммит** с исправлениями:
   ```bash
   git add -A
   git commit -m "fix: Fix Dispatcher initialization to create after Redis connection"
   ```

2. **Запушьте изменения**:
   ```bash
   git push -u origin claude/telegram-bot-implementation-011CUuzKi565NkHTBai51uXT
   ```

3. **Дополнительные улучшения** (опционально):
   - Добавьте обработку платежей (после установки yookassa)
   - Настройте AI провайдеры (OpenAI, Anthropic, Google)
   - Реализуйте систему рефералов
   - Добавьте админские команды

## Логи для отладки

Если возникли проблемы, соберите следующую информацию:

```bash
# Версии
python --version
pip list | grep -E "aiogram|sqlalchemy|redis|asyncpg"

# Статус сервисов
systemctl status postgresql redis-server

# Проверка подключений
psql -U ai_bot_user -d ai_bot -h localhost -c "SELECT 1;"
redis-cli ping

# Логи бота
python main.py 2>&1 | tee bot.log
```
