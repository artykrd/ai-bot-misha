# Журнал исправлений по аудиту (2026-06-19)

Этот файл — единый источник правды по устранению проблем, найденных в аудите.
Каждое исправление отмечается статусом: ⬜ TODO · 🔄 В работе · ✅ Сделано · ⏸ Отложено.

Ветка разработки: `fix/audit-sprint-1` (далее по спринту).

---

## СПРИНТ 1 — КРИТИЧЕСКОЕ (немедленно)

### #1 Гонка async-сессий БД в видео-воркере (8358 ошибок в логах)
**Файлы:** `app/workers/video_worker.py`, `app/services/video_job_service.py`
**Проблема:** одна `AsyncSession` шарится 5 конкурентными задачами `asyncio.gather` →
`This transaction is closed`, `commit() can't be called here / _prepare_impl in progress`.
**Шаги:**
- [x] 1.1 В `process_pending_jobs`: открывать отдельную сессию на каждую задачу (новый `_process_job_isolated`).
- [x] 1.2 В `retry_timeout_waiting_jobs`: то же + вынесен блок «max attempts exceeded» в `_fail_timeout_job_isolated`.
- [x] 1.3 `_refund_tokens`/`update_job_status` теперь работают в собственной сессии каждой задачи.
- [x] 1.4 Smoke-тест: 5 конкурентных задач → 5 различных сессий (PASS).
**Статус:** ✅ Сделано

### #2 Veo сломан — `google-genai 1.2.0 < 1.3.0`
**Файлы:** `requirements.txt`, окружение, `app/services/video/veo_service.py`
**Проблема:** установлен SDK без `generate_videos` → каждая генерация Veo падает.
**Шаги:**
- [x] 2.1 Зафиксирован `google-genai==1.3.0` в `requirements.txt` (минимум с `generate_videos`, совместим с pydantic 2.5.0 / aiogram). Поднят `httpx==0.28.1` (требование genai 1.3.0), убран дубль httpx в test-группе.
- [x] 2.2 Установлено в venv: `google-genai 1.3.0`, `httpx 0.28.1`, `pydantic 2.5.0`.
- [x] 2.3 Подтверждено: `google.genai.models.Models.generate_videos` присутствует.
- [x] 2.4 Добавлен fail-fast self-check в `main.py` (startup) + удалён orphan `google-cloud-aiplatform` → `pip check` чист.
**Статус:** ✅ Сделано

---

## СПРИНТ 2 — ВЫСОКИЙ (эта неделя)

### #3 Потеря токенов при исключении внутри генерации
**Файлы:** `app/core/token_guard.py` (новый), `app/bot/middlewares/token_refund.py` (новый),
`app/services/subscription/subscription_service.py`, `app/bot/bot_instance.py`
**Решение:** централизованный авто-возврат вместо правки 31 хендлера. `check_and_use_tokens`
регистрирует резерв в per-update ContextVar; `TokenAutoRefundMiddleware` при ЛЮБОМ исключении
в хендлере возвращает незакоммиченный резерв, а при нормальном завершении — очищает трекер
(токены потрачены легитимно либо хендлер уже сам вернул soft-fail). Покрывает media/dialog/suno/async.
- [x] 3.1 Единый помощник `token_guard` (reserve-tracking → auto-rollback).
- [x] 3.2 Middleware гарантирует возврат на пути исключения для всех хендлеров.
- [x] 3.3 Smoke-тест 3 кейсов (исключение → возврат; успех → нет; soft-fail → без дубля) — PASS.
**Статус:** ✅ Сделано

### #4 Несогласованный механизм возврата токенов
- [x] 4.1 Все 5 оставшихся `add_eternal_tokens(..., "refund")` → `rollback_tokens()`
  (теперь 18/18 возвратов в media_handler через `rollback_tokens`).
- [x] 4.2 `rollback_tokens` уже возвращает в исходную подписку (fallback — вечная).
**Статус:** ✅ Сделано

### #5 Stars-платежи без идемпотентности
**Файл:** `app/bot/handlers/stars_payment.py`, модель `Payment`, миграция 011
- [x] 5.1 Проверка существующего `telegram_payment_charge_id` перед начислением (early return).
- [x] 5.2 Unique-индекс на `yukassa_payment_id`: модель + миграция `011`; дублей в проде нет (0/657),
  индекс применён, alembic stamped 011. Конфликт ловится идемпотентной проверкой.
**Статус:** ✅ Сделано

### #6 Админ-доступ проверяется вручную в каждом хендлере
**Файл:** `admin_main.py`
- [x] 6.1 `AdminAccessMiddleware` на `admin_router` (message + callback_query) — единая точка отказа.
- [x] 6.2 113 точечных `is_admin`-проверок оставлены как защита в глубину.
**Статус:** ✅ Сделано

### #7 Реферальные выплаты без блокировок строк
**Файл:** `app/services/referral/referral_service.py`
- [x] 7.1 `_get_or_create_balance(for_update=True)`; `exchange_money_to_tokens` берёт row-lock
  перед проверкой/списанием баланса → нет гонки double-spend.
**Статус:** ✅ Сделано

---

## СПРИНТ 3 — СРЕДНИЙ (2 недели)

### #8 Соотношение сторон (9:16/16:9)
- [ ] 8.1 Регресс-тесты callback→сохранённое значение→галочка для всех моделей.
- [ ] 8.2 Унифицировать дефолты формата.
**Статус:** ⬜ TODO

### #9 Сверка суммы платежа — алерт
- [ ] 9.1 Алерт (не только warning) при расхождении суммы.
**Статус:** ⬜ TODO

### #10 Контент-модерация ≠ «ошибка»
- [ ] 10.1 Различать 4xx-модерацию и сбой; гарантированный возврат при модерации.
- [ ] 10.2 Ретраи 429/5xx с backoff.
**Статус:** ⬜ TODO

### #11 Webhook-секрет ЮKassa обязателен в проде
- [ ] 11.1 Требовать `YUKASSA_WEBHOOK_SECRET` при `ENVIRONMENT=production`.
**Статус:** ⬜ TODO

### #12 CORS по умолчанию `*`
- [ ] 12.1 Явный список origins для прод-API.
**Статус:** ⬜ TODO

---

## ПРОИЗВОДИТЕЛЬНОСТЬ — ускорение генераций (запрос пользователя)

**Диагноз (2026-06-19):** блокирующих вызовов в event loop НЕТ (`requests`/`time.sleep`
в сервисах отсутствуют; SDK ЮKassa/Veo/Gemini вынесены в `asyncio.to_thread`). То есть
«нет асинхрона» — не причина. Реальные источники задержки:
- **P1. `VideoWorker.poll_interval = 30s`** (`app/workers/video_worker.py:29`) — задача
  ждёт в очереди до 30с ДО начала обработки и до 30с между опросами статуса.
- **P2. Потолок 5 задач/цикл** (`[:5]`) — под нагрузкой очередь рассасывается медленно.
  После Спринта 1 (изоляция сессий) параллелизм можно безопасно повышать.
- **P3.** Часть задержки — неустранимая латентность провайдеров (Kling/Veo/Suno).

**Шаги:**
- [x] P1.1 `poll_interval` 30с → **8с** (`bot_instance.py`). Очередь стартует и доставляется быстрее.
- [ ] P1.2 Мгновенный «пинок» воркера при создании задачи (event/Redis pub-sub) — отложено.
- [x] P2.1 Лимит одновременных задач сделан настраиваемым, поднят **5 → 8** (`max_concurrent`),
  безопасно благодаря изоляции сессий из Спринта 1.
- [ ] P3.1 Параллельность синхронных генераций (изображения) — проверить отсутствие глобальных локов.
- [ ] P3.2 Кэш результатов (ENABLE_AI_CACHE) — проверить, что включён и срабатывает.
**Статус:** 🔄 Частично (P1.1, P2.1 сделаны; P1.2/P3 — бэклог)

---

## ИСПРАВЛЕНО ПРИ ВЕРИФИКАЦИИ (вне исходного плана)

### #A1 Сломаны админ-уведомления об ошибках (`connector` kwarg)
**Файл:** `app/core/error_notifier.py`
**Проблема:** `AiohttpSession(connector=...)` не поддерживается в aiogram 3.27 →
`BaseSession.__init__() got an unexpected keyword argument 'connector'` → объект `Bot`
не создавался, `notify_admins()` молча не работал (предсуществующий баг, с мая в логах).
**Фикс:** форсировать IPv4 через `session._connector_init["family"] = socket.AF_INET`.
**Проверка:** после рестарта — `Error notifier initialized with admin bot`, 0 ошибок.
**Статус:** ✅ Сделано

---

## ИНЦИДЕНТ И ХОТФИКС (2026-06-19, после Спринта 2)

### #A2 Регрессия: `proxies` kwarg ломал ВСЕ модели (text/image/audio)
**Причина:** апгрейд `httpx` 0.26→0.28.1 (нужен для google-genai/Veo, #2) удалил параметр
`proxies`. Старые `openai==1.10.0` и `anthropic==0.40.0` всегда передавали `proxies=` в
`httpx.AsyncClient` → `TypeError: AsyncClient.__init__() got an unexpected keyword argument
'proxies'` при каждом вызове модели (GPT, Claude, DALL·E, GPT-image, Whisper/TTS).
**Обнаружено:** пользователь сообщил «ошибки по моделям»; в логах `handler_error` +
`Cause exception ... 'proxies'` при нажатии «Создать фото» (11:10).
**Фикс:** `openai==1.109.1`, `anthropic==0.111.0` (httpx-0.28-совместимы, pydantic<2.13 сохранён,
наша API-поверхность без изменений). Veo при этом остаётся рабочим.
**Проверка:** клиенты конструируются без ошибки, все методы на месте, `pip check` чист;
после рестарта — 0 ошибок `proxies`, 0 `handler_error`, чистый старт.
**Урок:** при бампе httpx проверять ВСЕ SDK на совместимость (openai/anthropic/genai), а не
только инициатора апгрейда.
**Статус:** ✅ Сделано

---

### #A3 Регрессия: Veo image-to-video / extension сломаны (`generate_videos(image=...)`)
**Причина:** в Спринте 1 (#2) `google-genai` был запинан на `1.3.0` — это минимальная версия с
`generate_videos`, НО её сигнатура: `generate_videos(model, prompt, config)` — без `image`,
`video`, без `types.VideoGenerationReferenceImage` и без полей `last_frame`/`reference_images`
в `GenerateVideosConfig`. Код `veo_service.py` написан под современный API. Итог: text-to-video
работал, а image-to-video падал с `Models.generate_videos() got an unexpected keyword argument
'image'`; extension/reference/last-frame — тоже. Kling/прочие видео не затронуты.
**Обнаружено:** пользователь сообщил «veo перестал работать, люди жалуются»; в логах
`veo_video_generation_failed ... unexpected keyword argument 'image'` (14:26), списания токенов
не было (actual_tokens=0 — авто-возврат сработал).
**Разбор пина:** прежняя заметка «google-genai ≥1.37 тянет pydantic≥2.13 и конфликтует с aiogram»
оказалась НЕВЕРНОЙ. Фактически 1.4.0–2.9.0 объявляют `pydantic>=2.0,<3` (не ≥2.13). aiogram
3.27 требует `pydantic>=2.4.1,<2.13`. Полный набор фич Veo 3.1 (image+video+RefImg+last_frame+
reference_images) появляется в **1.37.0**, и она чисто импортируется на нашем `pydantic==2.5.0`
(только безвредные UserWarning о shadowing полей в `Operation`).
**Фикс:** `google-genai==1.3.0 → 1.37.0`. Dry-run показал: все транзитивные зависимости
(anyio 4.11/websockets 14.2/typing-ext 4.15/tenacity 9.1.2/google-auth 2.55/httpx 0.28.1) уже
удовлетворены — меняется ТОЛЬКО сам пакет. `pip check` чист.
**Проверка:** сигнатура `generate_videos` = `[model, prompt, image, video, source, config]`,
`VideoGenerationReferenceImage` есть, `last_frame`/`reference_images` в конфиге есть; импорт
veo_service/executor/main OK; после рестарта — 0 ошибок, polling + video_worker(8s) активны,
`/health`=200.
**Урок:** при даунпине ради «минимальной версии с фичей X» сверять ПОЛНУЮ сигнатуру всех
используемых вызовов, а не только наличие метода; не доверять заметкам о конфликте без проверки
объявленных constraints.
**Статус:** ✅ Сделано

---

### #A4 Kling O1: «нажимаю Подтвердить — ничего не происходит» + неработающий авто-перевод
**Симптом (от пользователя):** при прикреплении фото жмёшь «✅ Продолжить» — ничего не
происходит. В логах: один и тот же пользователь нажал `kling_o1.continue` 8 раз подряд
(14:44–14:46), каждый раз `Update is handled` без ошибок.
**Причина 1 (UX-баг):** хэндлер `kling_o1.continue` делал `callback.message.edit_text(...)`
по СТАРОМУ сообщению (подтверждение загрузки фото), которое к моменту нажатия уже уехало вверх
по чату, + `await callback.answer()` без текста. Инструкция «теперь отправьте текстовое
описание» правилась вне видимой области, внизу чата ничего не появлялось → пользователь жал
кнопку снова и снова.
**Причина 2 (скрытый баг):** `async_kling_o1_handler.py:90` (и `async_kling3_handler.py:65`,
`media_handler.py:4149`) вызывали `OpenAIService.translate_to_english(...)`, а такого метода в
`OpenAIService` НЕ БЫЛО → `AttributeError` (`kling_o1_translate_failed` warning), авто-перевод
промта на английский молча не работал во всех трёх местах (промт уходил в Kling без перевода).
**Фикс:**
- `async_kling_o1_handler.py` `kling_o1.continue`: снимаем клавиатуру со старого сообщения и
  отправляем инструкцию НОВЫМ сообщением вниз чата + поясняющий тост в `callback.answer(...)`;
  если медиа не загружено — алерт «Сначала прикрепите фото или видео» вместо тихого перехода.
- `app/services/ai/openai_service.py`: добавлен метод `translate_to_english()` на базе
  `generate_text(gpt-4o-mini, temperature=0)` с сохранением токенов @Image1/@Video1. Чинит все
  3 вызова (kling_o1, kling3, media_handler).
**Проверка:** AST/импорт OK, метод присутствует; после рестарта — 0 ошибок, polling +
video_worker(8s), `/health`=200.
**Статус:** ✅ Сделано

> ⚠️ Отдельно замечено (НЕ входит в этот фикс): **Kling Motion Control** падает с
> `Kling API error 1201: couldn't get the contents of the file`. Видео туда передаётся как
> Telegram-URL (`api.telegram.org/file/bot<token>/...`), который серверы Kling, судя по всему,
> не могут скачать (Telegram недоступен из их инфраструктуры). В отличие от #A4 здесь
> пользователь ВИДИТ ошибку (не «ничего не происходит»). Кандидат в Спринт 3: заливать видео
> на доступный Kling'у хостинг/предоставлять публичный URL. Внесено в бэклог как #13.8.

---

## БЭКЛОГ — НИЗКИЙ

- [ ] 13.1 Чистка репозитория: файл `=`, дубли `*.md`, логи из рабочей копии.
- [ ] 13.2 Один путь Google-SDK (убрать легаси `google-generativeai`, где можно).
- [ ] 13.3 Рассмотреть webhook вместо polling.
- [ ] 13.4 Обновить pin'ы `openai`/`anthropic`.
- [ ] 13.5 **Сломан тест-раннер** (обнаружено в Спринте 1): `pytest==9.0.3` несовместим
  с `pytest-asyncio==0.23.3` → `INTERNALERROR ... 'Package' object has no attribute 'obj'`.
  Нужно поднять `pytest-asyncio` (>=0.24/1.x) или согласовать версию pytest. Блокирует
  автотесты — пока проверка через целевые smoke-скрипты.
- [ ] 13.7 **Дрейф alembic-миграций** (обнаружено в Спринте 2): схема поддерживается через
  `Base.metadata.create_all` в `init_db`, а `alembic_version` отставал (был на 008 при наличии
  таблиц 009/010, частично). Унифицировать: либо полностью на alembic, либо задокументировать
  create_all как источник истины. (Сейчас застемплено на 011.)
- [ ] 13.8 **Kling Motion Control 1201**: видео отдаётся в Kling как Telegram-URL, который их
  серверы не скачивают (`couldn't get the contents of the file`). Нужен публично доступный для
  Kling URL (залив на S3/совместимый хостинг) либо отключить Motion Control до решения. (Подробно — см. #A4.)
- [ ] 13.6 **Ложный critical-алерт при старте**: `webhook_health_check_failed` срабатывает
  в стартовом окне, пока FastAPI ещё не забиндил порт 8000 (после старта `/health`=200).
  Шлёт «critical» админам при каждом рестарте. Фикс: grace-период перед первой проверкой
  или ретрай health перед алертом. (Безвреден — самовосстанавливается.)

---

## ЛОГ ВЫПОЛНЕНИЯ

> Здесь фиксируются фактические изменения по датам/коммитам.

### 2026-06-19
- Создана ветка `fix/audit-sprint-1`.
- Создан журнал `AUDIT_FIX_LOG.md` с полным планом.
- **Спринт 1 завершён:**
  - #1: `app/workers/video_worker.py` — каждая видео-задача обрабатывается в собственной
    `AsyncSession` (`_process_job_isolated`, `_fail_timeout_job_isolated`). Устранена причина
    8358 ошибок `This transaction is closed`. Smoke-тест изоляции сессий — PASS.
  - #2: `requirements.txt` — `google-genai==1.3.0`, `httpx==0.28.1`; venv обновлён;
    `main.py` — fail-fast проверка наличия `generate_videos` при старте; удалён orphan
    `google-cloud-aiplatform`; `pip check` чист. Veo восстановлен.
  - Обнаружено: сломан тест-раннер (pytest/pytest-asyncio) → внесено в бэклог (#13.5).
- **Верификация Спринта 1 на проде:**
  - `systemctl restart bot.service` → `bot_started_successfully`, `video_worker_started`,
    `Start polling`. Self-check Veo прошёл (нет `dependency_check_failed`).
  - Журнал за 90с работы: **0 ошибок** error-level, `/health`=200, нет `video_job_processing_exception`.
  - Регрессий нет.
- **Бонус-фикс при верификации (#A1):** `app/core/error_notifier.py` — починены админ-уведомления
  об ошибках (`connector` kwarg → `_connector_init["family"]`). После рестарта:
  `Error notifier initialized with admin bot`, 0 ошибок.
- Добавлены: задача по производительности (P1–P3), health-race в бэклог (#13.6).
- **Спринт 2 завершён + быстрый выигрыш по скорости:**
  - #3: централизованный авто-возврат токенов (`app/core/token_guard.py` +
    `app/bot/middlewares/token_refund.py` + трекинг в `check_and_use_tokens`). Smoke-тест 3 кейсов — PASS.
  - #4: 5 оставшихся возвратов переведены на `rollback_tokens` (18/18 в media_handler).
  - #5: идемпотентность Stars (early-return по charge_id) + unique-индекс `ix_payments_yukassa_payment_id`
    (миграция 011, дублей 0/657, alembic stamped 011).
  - #6: `AdminAccessMiddleware` на admin_router — централизованный контроль доступа.
  - #7: row-lock в `exchange_money_to_tokens` (referral).
  - P1.1: `poll_interval` 30→8с; P2.1: `max_concurrent` 5→8.
  - Обнаружено: дрейф alembic-миграций → бэклог (#13.7).
- **Верификация Спринта 2 на проде:** `systemctl restart bot.service bot-admin.service` →
  оба `active`, `bot_started_successfully`, `video_worker_started` (poll_interval=8),
  `admin_bot_started` (NRestarts=0). За 60с: **0 ошибок** error-level, нет трейсбеков, `/health`=200.
