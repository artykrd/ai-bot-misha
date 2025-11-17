# 🚀 Production Deployment Checklist

**Версия:** 1.0
**Дата:** 2025-11-17

---

## ✅ Пре-деплой чеклист

### 1. API Ключи (**КРИТИЧНО**)

```bash
# Проверьте, что все ключи настроены в .env
grep "API_KEY" .env | grep -v "^#" | grep -v "sk-\.\.\."
```

**Обязательные:**
- [ ] `OPENAI_API_KEY` - OpenAI (GPT-4, GPT-4o-mini)
- [ ] `TELEGRAM_BOT_TOKEN` - Основной бот
- [ ] `TELEGRAM_ADMIN_BOT_TOKEN` - Админ бот
- [ ] `DATABASE_URL` - PostgreSQL
- [ ] `REDIS_URL` - Redis
- [ ] `SECRET_KEY` - Безопасность (сгенерировать новый!)

**Рекомендуемые (высокий ROI):**
- [ ] `ANTHROPIC_API_KEY` - Claude (топовое качество)
- [ ] `GOOGLE_AI_API_KEY` - Gemini Flash (самый дешевый!)
- [ ] `DEEPSEEK_API_KEY` - DeepSeek (19,000% маржа!)
- [ ] `PERPLEXITY_API_KEY` - Sonar (поиск в интернете)

**Опциональные:**
- [ ] `YUKASSA_SHOP_ID` + `YUKASSA_SECRET_KEY` - Платежи
- [ ] `SENTRY_DSN` - Мониторинг ошибок

---

### 2. База данных

```bash
# Проверить подключение
python -c "from app.database.database import init_db; import asyncio; asyncio.run(init_db())"

# Применить миграции
alembic upgrade head

# Создать тестового пользователя с безлимитом
psql -d ai_bot -c "SELECT id, telegram_id, username FROM users LIMIT 5;"
```

**Чеклист БД:**
- [ ] PostgreSQL 15+ установлен
- [ ] БД создана
- [ ] Миграции применены
- [ ] Тестовый пользователь создан
- [ ] Backup настроен (pg_dump cron)

---

### 3. Redis

```bash
# Проверить статус
systemctl status redis-server

# Проверить подключение
redis-cli ping
```

**Чеклист Redis:**
- [ ] Redis 7+ установлен
- [ ] Сервис запущен
- [ ] Подключение работает

---

### 4. Тестирование

```bash
# Запустить полный тест
source venv/bin/activate
python scripts/comprehensive_test.py

# Проверить результаты
cat test_reports/test_results_*.md | tail -50
```

**Критерии успеха:**
- [ ] Все API ключи configured
- [ ] БД подключена
- [ ] Все модели работают (или skipped если ключ не настроен)
- [ ] 0 критических ошибок
- [ ] < 5 warnings

---

### 5. Конфигурация

```bash
# Проверить .env файл
grep "ENVIRONMENT" .env
grep "DEBUG" .env
grep "LOG_LEVEL" .env
```

**Production настройки (.env):**
```env
# ОБЯЗАТЕЛЬНО для production!
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Безопасность
SECRET_KEY=<сгенерировать новый 50+ символов>
CORS_ORIGINS=https://yourdomain.com

# Rate limiting
FREE_USER_RATE_LIMIT=5
BASIC_RATE_LIMIT=100
PREMIUM_RATE_LIMIT=500
```

**Генерация SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(50))
```

---

### 6. Логирование

```bash
# Создать директорию для логов
mkdir -p logs
chmod 755 logs

# Проверить ротацию логов (logrotate)
sudo nano /etc/logrotate.d/aibot
```

**logrotate конфиг:**
```
/opt/bot/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
}
```

---

## 🚀 Деплой

### Вариант 1: Systemd (рекомендуется)

#### 1. Создать systemd сервисы

```bash
# Основной бот
sudo nano /etc/systemd/system/aibot.service
```

```ini
[Unit]
Description=AI Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bot
Environment="PATH=/opt/bot/venv/bin"
ExecStart=/opt/bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Админ бот
sudo nano /etc/systemd/system/aibot-admin.service
```

```ini
[Unit]
Description=AI Telegram Bot - Admin
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bot
Environment="PATH=/opt/bot/venv/bin"
ExecStart=/opt/bot/venv/bin/python admin_main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Запуск сервисов

```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable aibot aibot-admin

# Запустить
sudo systemctl start aibot aibot-admin

# Проверить статус
sudo systemctl status aibot
sudo systemctl status aibot-admin

# Просмотр логов
sudo journalctl -u aibot -f
sudo journalctl -u aibot-admin -f
```

---

### Вариант 2: Screen (для тестирования)

```bash
# Создать screen сессию для основного бота
screen -S aibot
source venv/bin/activate
python main.py
# Ctrl+A+D для отсоединения

# Создать screen сессию для админ бота
screen -S aibot-admin
source venv/bin/activate
python admin_main.py
# Ctrl+A+D для отсоединения

# Просмотр сессий
screen -ls

# Подключиться к сессии
screen -r aibot
```

---

## ✅ Пост-деплой проверки

### 1. Проверка работы бота

```bash
# Отправить /start боту в Telegram
# Проверить что:
```

- [ ] Бот отвечает на `/start`
- [ ] Показывает правильный баланс токенов
- [ ] Все кнопки работают (не краш)
- [ ] Выбор модели работает
- [ ] Диалог начинается
- [ ] AI отвечает на запросы
- [ ] Токены списываются

### 2. Проверка логов

```bash
# Проверить логи на ошибки
tail -f logs/bot.log | grep ERROR
tail -f logs/bot.log | grep CRITICAL

# Должно быть пусто или минимум ошибок
```

- [ ] Нет CRITICAL ошибок
- [ ] Нет повторяющихся ERROR
- [ ] INFO логи выглядят нормально

### 3. Мониторинг

```bash
# Проверить использование ресурсов
htop

# Проверить использование БД
psql -d ai_bot -c "SELECT COUNT(*) FROM users;"
psql -d ai_bot -c "SELECT COUNT(*) FROM subscriptions;"

# Проверить Redis
redis-cli
> DBSIZE
> INFO stats
```

**Нормальные значения:**
- RAM: < 500MB на бот
- CPU: < 5% в idle, < 50% при нагрузке
- Disk: проверить свободное место

### 4. Тестирование под нагрузкой

```bash
# Создать 10 тестовых пользователей
# Отправить по 5 запросов от каждого
# Проверить что все работает без ошибок
```

- [ ] Бот отвечает всем пользователям
- [ ] Нет задержек > 10 секунд
- [ ] Токены списываются корректно
- [ ] Логи без ошибок

---

## 🔒 Безопасность

### Обязательно:

- [ ] Сменить `SECRET_KEY` на production значение
- [ ] Использовать сложные пароли БД
- [ ] Настроить firewall (UFW):
  ```bash
  sudo ufw allow 22/tcp      # SSH
  sudo ufw allow 443/tcp     # HTTPS (если используете webhook)
  sudo ufw enable
  ```
- [ ] Регулярно обновлять зависимости:
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- [ ] Настроить fail2ban для SSH
- [ ] Ограничить доступ к БД (только localhost)

### Рекомендуется:

- [ ] Настроить HTTPS для webhook (если используете)
- [ ] Включить Sentry для мониторинга ошибок
- [ ] Настроить автоматические бэкапы БД:
  ```bash
  # crontab -e
  0 3 * * * pg_dump ai_bot > /backup/ai_bot_$(date +\%Y\%m\%d).sql
  ```
- [ ] Настроить мониторинг (Prometheus + Grafana)

---

## 📊 Мониторинг и алерты

### Что мониторить:

1. **Uptime бота**
   ```bash
   # Добавить healthcheck endpoint
   curl http://localhost:8000/health
   ```

2. **Использование API квот**
   - OpenAI: https://platform.openai.com/usage
   - Anthropic: https://console.anthropic.com/settings/cost
   - Google: https://console.cloud.google.com/billing

3. **Ошибки в логах**
   ```bash
   # Настроить алерт на CRITICAL/ERROR
   tail -f logs/bot.log | grep -E "CRITICAL|ERROR"
   ```

4. **Использование токенов пользователями**
   ```sql
   -- Топ-10 пользователей по использованию
   SELECT u.telegram_id, u.username, SUM(s.tokens_used) as total
   FROM users u
   JOIN subscriptions s ON u.id = s.user_id
   GROUP BY u.id
   ORDER BY total DESC
   LIMIT 10;
   ```

---

## 🆘 Troubleshooting

### Бот не запускается

```bash
# Проверить логи
sudo journalctl -u aibot -n 50

# Проверить .env
cat .env | grep -v "^#" | grep -v "^$"

# Проверить БД
pg_isready -h localhost -p 5432

# Проверить Redis
redis-cli ping
```

### Бот крашится

```bash
# Проверить последние логи
tail -100 logs/bot.log

# Проверить use ресурсов
htop

# Перезапустить
sudo systemctl restart aibot
```

### AI не отвечает

```bash
# Проверить API ключи
python scripts/comprehensive_test.py --models-only

# Проверить квоты API
# OpenAI: https://platform.openai.com/usage
# Anthropic: https://console.anthropic.com/

# Проверить логи
tail -f logs/bot.log | grep "openai_text"
```

### Токены не списываются

```bash
# Проверить БД
psql -d ai_bot

SELECT * FROM subscriptions WHERE is_active = true LIMIT 5;

# Проверить логи
tail -f logs/bot.log | grep "tokens_used"
```

---

## 📝 Maintenance

### Еженедельно:

- [ ] Проверить логи на ошибки
- [ ] Проверить использование disk space
- [ ] Проверить квоты API
- [ ] Проверить статистику пользователей

### Ежемесячно:

- [ ] Обновить зависимости (pip install --upgrade -r requirements.txt)
- [ ] Очистить старые логи
- [ ] Проверить бэкапы БД
- [ ] Ревью безопасности

### При каждом деплое:

- [ ] Запустить тесты
- [ ] Проверить миграции БД
- [ ] Создать тег в git
- [ ] Обновить CHANGELOG

---

## ✅ Production Ready Checklist (финальный)

**Критические (должны быть ✅):**
- [ ] Все API ключи настроены
- [ ] БД работает
- [ ] Redis работает
- [ ] Тесты проходят (0 критических ошибок)
- [ ] SECRET_KEY изменен
- [ ] ENVIRONMENT=production
- [ ] DEBUG=False
- [ ] Логи работают
- [ ] Systemd сервисы созданы и запущены
- [ ] Бот отвечает на /start
- [ ] AI модели работают

**Важные (сильно рекомендуется):**
- [ ] Бэкапы БД настроены
- [ ] Firewall настроен
- [ ] Мониторинг настроен
- [ ] Sentry подключен
- [ ] Платежная система настроена (если нужна)

**Опциональные (можно добавить потом):**
- [ ] HTTPS/Webhook
- [ ] Prometheus + Grafana
- [ ] CI/CD pipeline
- [ ] Docker контейнеризация

---

## 🎯 Готов к production?

Если все пункты из "Критические" отмечены ✅ - **ДА, можно запускать!**

Запуск в продакшен:
```bash
# Финальная проверка
python scripts/comprehensive_test.py

# Если тесты прошли - запускаем
sudo systemctl start aibot aibot-admin

# Проверяем
sudo systemctl status aibot
```

**Поздравляю! 🎉 Бот в production!**

---

*Последнее обновление: 2025-11-17*
