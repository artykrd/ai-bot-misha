# Интеграция логирования AI-операций

## Обзор

Система логирования AI-операций позволяет отслеживать все запросы к AI-сервисам с полной информацией о стоимости.

**Ключевые принципы:**
- Логирование работает параллельно с существующим кодом
- Ошибки логирования не блокируют основные операции
- Стоимость берётся из БД (таблица `model_costs`)
- Backward-compatible: старый код продолжает работать

## Быстрый старт

### 1. Импорт

```python
from app.services.logging import log_ai_operation_background
```

### 2. Добавление логирования после успешной операции

```python
# После успешного выполнения AI-операции:
log_ai_operation_background(
    user_id=user.id,
    model_id="suno",  # ID модели из model_costs
    operation_category="audio_gen",  # Категория операции
    tokens_cost=17600,  # Токены, списанные с пользователя
    prompt=song_title[:500],  # Опционально: текст запроса
    status="completed",  # completed или failed
    response_file_path=audio_path,  # Путь к результату
    processing_time_seconds=elapsed_time,  # Время обработки
    input_data={"style": style, "version": model_version},  # Доп. параметры
)
```

## Категории операций

| Категория | Описание | Примеры моделей |
|-----------|----------|-----------------|
| `text` | Текстовая генерация | gpt-4o, claude-4, gemini-pro |
| `text_with_image` | Vision модели | gpt-4o (с изображением) |
| `image_gen` | Генерация изображений | dalle3, midjourney, nano-banana |
| `image_edit` | Редактирование изображений | upscale, remove-bg, face-swap |
| `video_gen` | Генерация видео | sora2, kling-2.5, veo-3.1 |
| `audio_gen` | Генерация музыки | suno |
| `transcription` | Расшифровка аудио | whisper |
| `tts` | Синтез речи | openai-tts |

## Примеры интеграции

### Suno (генерация музыки)

```python
# В suno_handler.py, после успешной генерации:

import time
from app.services.logging import log_ai_operation_background

# ... существующий код генерации ...

start_time = time.time()

# Генерация
result = await suno_service.generate_music(
    prompt=style,
    lyrics=lyrics,
    model_version=model_version,
    is_instrumental=is_instrumental,
)

elapsed_time = int(time.time() - start_time)

# Логирование (fire-and-forget)
if result.get("audio_url"):
    log_ai_operation_background(
        user_id=user.id,
        model_id="suno",
        operation_category="audio_gen",
        tokens_cost=tokens_cost,
        prompt=f"{song_title}: {style}"[:500],
        status="completed",
        response_file_path=result.get("audio_url"),
        processing_time_seconds=elapsed_time,
        input_data={
            "model_version": model_version,
            "is_instrumental": is_instrumental,
            "style": style,
        },
    )
else:
    log_ai_operation_background(
        user_id=user.id,
        model_id="suno",
        operation_category="audio_gen",
        tokens_cost=tokens_cost,
        prompt=f"{song_title}: {style}"[:500],
        status="failed",
        error_message=result.get("error", "Unknown error"),
        processing_time_seconds=elapsed_time,
    )
```

### Kling (генерация видео)

```python
from app.services.logging import log_ai_operation_background

# ... существующий код ...

start_time = time.time()

# Генерация видео
video_result = await kling_service.generate_video(
    prompt=prompt,
    version=kling_settings.version,
    duration=kling_settings.duration,
    aspect_ratio=kling_settings.aspect_ratio,
)

elapsed_time = int(time.time() - start_time)

# Определяем model_id на основе версии
model_id = f"kling-{kling_settings.version.lower()}"

# Логирование
log_ai_operation_background(
    user_id=user.id,
    model_id=model_id,
    operation_category="video_gen",
    tokens_cost=estimated_tokens,
    prompt=prompt[:500],
    status="completed" if video_result else "failed",
    response_file_path=video_result.get("video_url") if video_result else None,
    processing_time_seconds=elapsed_time,
    input_data={
        "version": kling_settings.version,
        "duration": kling_settings.duration,
        "aspect_ratio": kling_settings.aspect_ratio,
    },
)
```

### Whisper (транскрипция)

```python
from app.services.logging import log_ai_operation_background

# ... существующий код ...

start_time = time.time()

# Транскрипция
transcription = await openai_audio_service.transcribe(
    audio_path=audio_path,
)

elapsed_time = int(time.time() - start_time)

# Расчёт стоимости: tokens = минуты * 500
audio_duration_minutes = audio_duration_seconds / 60
tokens_cost = int(audio_duration_minutes * 500)

# Логирование
log_ai_operation_background(
    user_id=user.id,
    model_id="whisper",
    operation_category="transcription",
    tokens_cost=tokens_cost,
    status="completed",
    processing_time_seconds=elapsed_time,
    input_data={
        "audio_duration_minutes": audio_duration_minutes,
    },
)
```

## Асинхронное логирование

Для случаев, когда нужно дождаться результата логирования:

```python
from app.services.logging import log_ai_operation

# Вернёт ID записи или None при ошибке
ai_request_id = await log_ai_operation(
    user_id=user.id,
    model_id="dalle3",
    operation_category="image_gen",
    tokens_cost=9500,
    prompt=prompt[:500],
    status="completed",
)

if ai_request_id:
    logger.info("logged_ai_request", id=ai_request_id)
```

## Обновление статуса

Для длительных операций можно создать запись в статусе "pending", а затем обновить:

```python
from app.services.logging import AILoggingService

async with async_session_maker() as session:
    logging_service = AILoggingService(session)

    # Создаём запись в pending
    ai_request_id = await logging_service.log_operation(
        user_id=user.id,
        model_id="sora2",
        operation_category="video_gen",
        tokens_cost=50000,
        status="pending",
    )

    # ... выполняем генерацию ...

    # Обновляем статус
    await logging_service.update_operation_status(
        ai_request_id=ai_request_id,
        status="completed",
        response_file_path=video_path,
        processing_time_seconds=elapsed_time,
    )
```

## Добавление новых моделей

Новые модели добавляются в таблицу `model_costs`:

```sql
INSERT INTO model_costs (
    model_id, provider, category_code, display_name,
    cost_usd_per_unit, cost_unit, tokens_per_unit,
    unlimited_daily_limit
) VALUES (
    'new-model-id', 'provider-name', 'video_gen', 'New Model Name',
    0.50, 'request', 50000,
    30  -- лимит для безлимита
);
```

Код не нужно менять - логирование автоматически подхватит стоимость из БД.

## Мониторинг

После интеграции данные будут доступны:

1. **В ежедневных отчётах** (09:00 MSK)
2. **Через SQL-запросы**:

```sql
-- Топ моделей по себестоимости за день
SELECT
    ai_model,
    COUNT(*) as requests,
    SUM(cost_usd) as total_cost_usd,
    SUM(cost_rub) as total_cost_rub
FROM ai_requests
WHERE created_at >= NOW() - INTERVAL '1 day'
    AND status = 'completed'
GROUP BY ai_model
ORDER BY total_cost_usd DESC;

-- Анализ безлимитных подписок
SELECT
    subscription_id,
    COUNT(*) as requests,
    SUM(tokens_cost) as total_tokens,
    SUM(cost_rub) as total_cost_rub
FROM ai_requests
WHERE is_unlimited_subscription = true
    AND created_at >= NOW() - INTERVAL '1 day'
GROUP BY subscription_id;
```

## Приоритет интеграции

1. **Критичный** (видео - высокая себестоимость):
   - Sora
   - Kling
   - Veo
   - Luma
   - Hailuo

2. **Высокий** (аудио):
   - Suno
   - Whisper
   - TTS

3. **Средний** (изображения):
   - DALL-E
   - Midjourney
   - Stability AI

4. **Низкий** (текст - уже частично логируется):
   - GPT-4
   - Claude
   - Gemini
