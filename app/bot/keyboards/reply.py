"""
Reply keyboards for the bot.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    """Minimal main menu reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Создать фото"), KeyboardButton(text="🎬 Создать видео")],
            [KeyboardButton(text="🎵 Аудио"), KeyboardButton(text="💬 AI Чат")],
            [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="💎 Подписка")],
        ],
        resize_keyboard=True
    )
