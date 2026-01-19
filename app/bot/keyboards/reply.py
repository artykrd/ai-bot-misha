"""
Reply keyboards for the bot.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Minimal main menu reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Создать видео"), KeyboardButton(text="💬 Диалоги")],
            [KeyboardButton(text="🎨 Работа с фото"), KeyboardButton(text="🖼 Создать фото")],
            [KeyboardButton(text="🤖 Выбрать модель"), KeyboardButton(text="🎧 Работа с аудио")],
            [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="💎 Подписка")],
            [KeyboardButton(text="🤝 Партнерство"), KeyboardButton(text="🆘 Поддержка")],
        ],
        resize_keyboard=True
    )
