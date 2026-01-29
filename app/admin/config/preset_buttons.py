"""
Preset buttons configuration for broadcast messages.
Contains ready-to-use buttons organized by categories.
"""

PRESET_BUTTONS = {
    "ai_models": {
        "name": "🤖 AI Модели",
        "description": "Текстовые AI модели для диалогов",
        "buttons": [
            {
                "text": "GPT 4o",
                "callback_data": "bot.start_chatgpt_dialog_325",
                "description": "OpenAI GPT-4o - мощная модель"
            },
            {
                "text": "Claude 4",
                "callback_data": "bot.start_chatgpt_dialog_333",
                "description": "Anthropic Claude 4 - умная модель"
            },
            {
                "text": "GPT 5 Mini",
                "callback_data": "bot.start_chatgpt_dialog_337",
                "description": "OpenAI GPT-5 Mini - быстрая модель"
            },
            {
                "text": "Deepseek R1",
                "callback_data": "bot.start_chatgpt_dialog_328",
                "description": "Deepseek R1 - reasoning модель"
            },
            {
                "text": "Deepseek Chat",
                "callback_data": "bot.start_chatgpt_dialog_327",
                "description": "Deepseek Chat - диалоговая модель"
            },
            {
                "text": "Gemini Flash 2.0",
                "callback_data": "bot.start_chatgpt_dialog_329",
                "description": "Google Gemini Flash 2.0"
            },
            {
                "text": "O3 Mini",
                "callback_data": "bot.start_chatgpt_dialog_326",
                "description": "OpenAI O3 Mini"
            },
            {
                "text": "GPT 4.1 Mini",
                "callback_data": "bot.start_chatgpt_dialog_324",
                "description": "OpenAI GPT-4.1 Mini"
            },
        ]
    },

    "creative": {
        "name": "🎨 Креатив",
        "description": "Генерация изображений, видео, музыки",
        "buttons": [
            {
                "text": "DALL-E 3",
                "callback_data": "bot.gpt_image",
                "description": "Генерация изображений через DALL-E 3"
            },
            {
                "text": "Midjourney",
                "callback_data": "bot.midjourney",
                "description": "Генерация через Midjourney"
            },
            {
                "text": "Nano Banana",
                "callback_data": "bot.nano",
                "description": "Nano Banana - быстрая генерация изображений"
            },
            {
                "text": "Nano Banana PRO",
                "callback_data": "bot.nano_pro",
                "description": "Nano Banana PRO - улучшенная версия"
            },
            {
                "text": "Sora Video",
                "callback_data": "bot.sora",
                "description": "Генерация видео через Sora"
            },
            {
                "text": "Kling Video",
                "callback_data": "bot.kling_main",
                "description": "Генерация видео через Kling"
            },
            {
                "text": "Suno Music",
                "callback_data": "bot.suno",
                "description": "Создание музыки через Suno"
            },
        ]
    },

    "subscription": {
        "name": "💎 Подписка",
        "description": "Покупка подписки и токенов",
        "buttons": [
            {
                "text": "Купить подписку",
                "callback_data": "bot#shop",
                "description": "Открыть магазин подписок"
            },
            {
                "text": "Вечные токены",
                "callback_data": "bot#shop_tokens",
                "description": "Купить вечные токены"
            },
            {
                "text": "Реферальная программа",
                "callback_data": "bot.refferal_program",
                "description": "Пригласить друзей и получить токены"
            },
        ]
    },

    "tools": {
        "name": "🛠 Инструменты",
        "description": "Дополнительные инструменты",
        "buttons": [
            {
                "text": "Whisper (транскрибация)",
                "callback_data": "bot.whisper",
                "description": "Транскрибация речи в текст"
            },
            {
                "text": "Фото инструменты",
                "callback_data": "bot.pi",
                "description": "Инструменты для работы с фото"
            },
            {
                "text": "Face Swap",
                "callback_data": "bot.faceswap",
                "description": "Замена лица на фото"
            },
        ]
    },

    "navigation": {
        "name": "📋 Навигация",
        "description": "Меню и навигация по боту",
        "buttons": [
            {
                "text": "Главное меню",
                "callback_data": "bot.back",
                "description": "Вернуться в главное меню"
            },
            {
                "text": "AI Модели",
                "callback_data": "bot.llm_models",
                "description": "Список всех AI моделей"
            },
            {
                "text": "Профиль",
                "callback_data": "bot.profile",
                "description": "Показать профиль пользователя"
            },
            {
                "text": "Диалоги",
                "callback_data": "bot.dialogs_chatgpt",
                "description": "История диалогов"
            },
            {
                "text": "Активировать промокод",
                "callback_data": "activate_promocode",
                "description": "Ввести промокод"
            },
            {
                "text": "Помощь",
                "callback_data": "help",
                "description": "Показать справку"
            },
        ]
    },
}


def get_category_names() -> list[tuple[str, str]]:
    """
    Get list of category keys and names for keyboard display.

    Returns:
        List of tuples: [(key, name), ...]
    """
    return [(key, data["name"]) for key, data in PRESET_BUTTONS.items()]


def get_category_buttons(category_key: str) -> list[dict]:
    """
    Get buttons for specific category.

    Args:
        category_key: Category key from PRESET_BUTTONS

    Returns:
        List of button dicts with text, callback_data, description
    """
    return PRESET_BUTTONS.get(category_key, {}).get("buttons", [])


def get_button_by_callback(callback_data: str) -> dict | None:
    """
    Find button by callback_data across all categories.

    Args:
        callback_data: Callback data to search for

    Returns:
        Button dict if found, None otherwise
    """
    for category in PRESET_BUTTONS.values():
        for button in category["buttons"]:
            if button["callback_data"] == callback_data:
                return button
    return None
