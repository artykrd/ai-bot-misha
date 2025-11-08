# AI Models Integration

## Обзор

Бот поддерживает интеграцию с несколькими AI провайдерами через унифицированный интерфейс. Система автоматически определяет, какой сервис использовать в зависимости от выбранной модели.

## Поддерживаемые модели

### OpenAI (GPT)

- **GPT-4 Omni** (`gpt-4`)
  - Самая продвинутая модель OpenAI
  - Стоимость: 1,000 токенов за запрос
  - API модель: `gpt-4-turbo-preview`

- **GPT-4 Omni Mini** (`gpt-4-mini`)
  - Быстрая и доступная модель
  - Стоимость: 250 токенов за запрос
  - API модель: `gpt-4-0125-preview`

### Anthropic (Claude)

- **Claude 3.5 Sonnet** (`claude`)
  - Модель от Anthropic
  - Стоимость: 1,200 токенов за запрос
  - API модель: `claude-3-5-sonnet-20241022`

### Google (Gemini)

- **Gemini Pro** (`gemini`)
  - Модель от Google
  - Стоимость: 900 токенов за запрос
  - API модель: `gemini-pro`

### DeepSeek

- **DeepSeek V2** (`deepseek`)
  - Отличная альтернатива
  - Стоимость: 800 токенов за запрос
  - API модель: `deepseek-chat`

## Архитектура

### AI Service Factory

Фабрика автоматически выбирает правильный AI сервис на основе модели:

```python
from app.services.ai.ai_factory import AIServiceFactory

# Автоматический выбор сервиса
response = await AIServiceFactory.generate_text(
    model="gpt-4",
    prompt="Hello, how are you?"
)
```

### Mock Service

Если API ключи не настроены, система автоматически использует Mock Service, который возвращает тестовые ответы:

```python
# Принудительное использование mock
response = await AIServiceFactory.generate_text(
    model="gpt-4",
    prompt="Test",
    use_mock=True
)

# Проверка что используется mock
if response.metadata.get("mock"):
    print("Using mock service")
```

## Настройка API ключей

Добавьте API ключи в `.env` файл:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google AI
GOOGLE_AI_API_KEY=...

# DeepSeek
DEEPSEEK_API_KEY=...
```

## Базовый интерфейс

Все AI сервисы реализуют единый интерфейс `BaseAIProvider`:

```python
class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text response."""
        pass

    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Generate image from prompt."""
        pass
```

### AIResponse

Стандартный формат ответа:

```python
@dataclass
class AIResponse:
    success: bool
    content: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0
    metadata: dict = None
```

## Использование в хендлерах

### Пример обработки текстового запроса

```python
from app.services.ai.ai_factory import AIServiceFactory

async def process_ai_request(message: Message, state: FSMContext):
    # Получить выбранную модель из state
    data = await state.get_data()
    model = data.get("ai_model", "gpt-4")

    # Отправить запрос
    response = await AIServiceFactory.generate_text(
        model=model,
        prompt=message.text
    )

    if response.success:
        await message.answer(response.content)
    else:
        await message.answer(f"Error: {response.error}")
```

## Добавление новой модели

### 1. Создайте сервис

```python
# app/services/ai/your_service.py
from app.services.ai.base import BaseAIProvider, AIResponse

class YourService(BaseAIProvider):
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        # Ваша реализация
        pass
```

### 2. Добавьте в фабрику

```python
# app/services/ai/ai_factory.py
MODEL_PROVIDERS = {
    # ...
    "your-model": "your_provider",
}
```

### 3. Обновите клавиатуру

```python
# app/bot/keyboards/inline.py
def ai_models_keyboard():
    builder.row(
        InlineKeyboardButton(
            text="Your Model",
            callback_data="model:your-model"
        )
    )
```

### 4. Добавьте в text_ai.py

```python
# app/bot/handlers/text_ai.py
costs = {
    # ...
    "your-model": 500,
}

model_names = {
    # ...
    "your-model": "Your Model Name",
}
```

## Тестирование

### Запуск тестов

```bash
# Все AI тесты
pytest tests/test_bot_integration.py -v

# Только тесты моделей
pytest tests/test_bot_integration.py::TestAIModelSelection -v
```

### Тестирование без API ключей

Все тесты работают с mock сервисами:

```bash
# Тесты используют use_mock=True автоматически
pytest tests/test_bot_integration.py
```

### Ручное тестирование в боте

1. Запустите бота: `python main.py`
2. Отправьте `/start`
3. Нажмите "🤖 Выбрать модель"
4. Выберите модель (например, GPT-4)
5. Отправьте текстовое сообщение
6. Бот ответит тестовым сообщением с пометкой о mock режиме

## Обработка ошибок

### Отсутствующий API ключ

```python
# Автоматически используется mock
response = await AIServiceFactory.generate_text(
    model="gpt-4",
    prompt="test"
)
# response будет от MockAIService если OPENAI_API_KEY не задан
```

### Ошибка API

```python
response = await service.generate_text(prompt="test")

if not response.success:
    logger.error("ai_error", error=response.error)
    await message.answer(f"Ошибка: {response.error}")
```

## Мониторинг

Все AI запросы логируются:

```python
logger.info(
    "ai_request_completed",
    user_id=user.id,
    model=ai_model,
    tokens=tokens_cost,
    processing_time=response.processing_time,
    is_mock=response.metadata.get("mock", False)
)
```

## Оптимизация

### Кеширование

```python
# TODO: Реализовать кеширование популярных запросов
# См. настройки в config.py:
# - enable_ai_cache
# - ai_cache_ttl_hours
```

### Rate Limiting

Используется система токенов для ограничения частоты запросов.

## Production Checklist

- [ ] Настроены все необходимые API ключи
- [ ] Проверены лимиты API провайдеров
- [ ] Настроен мониторинг ошибок
- [ ] Реализовано кеширование (опционально)
- [ ] Настроены алерты на превышение квот
- [ ] Проверена стоимость токенов для всех моделей
