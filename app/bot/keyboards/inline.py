"""
Inline keyboards for the bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🗯 ChatGPT", callback_data="chatgpt"),
        InlineKeyboardButton(text="🍌 Nano Banana", callback_data="nano_banana")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Выбрать модель", callback_data="select_model"),
        InlineKeyboardButton(text="💬 Диалоги", callback_data="dialogs")
    )
    builder.row(
        InlineKeyboardButton(text="🌄 Создать фото", callback_data="create_photo"),
        InlineKeyboardButton(text="🎞 Создать видео", callback_data="create_video")
    )
    builder.row(
        InlineKeyboardButton(text="✂️ Работа с фото", callback_data="photo_tools"),
        InlineKeyboardButton(text="🎙 Работа с аудио", callback_data="audio_tools")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile"),
        InlineKeyboardButton(text="💎 Подписка", callback_data="subscription")
    )
    builder.row(
        InlineKeyboardButton(text="🤝🏼 Партнерство", callback_data="referral"),
        InlineKeyboardButton(text="🆘 Поддержка", url="https://t.me/support")
    )

    return builder.as_markup()


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Back to main menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="main_menu"))
    return builder.as_markup()


def subscription_keyboard() -> InlineKeyboardMarkup:
    """Subscription selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="7 дней — 150,000 токенов — 98 руб.",
            callback_data="buy:7days"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="14 дней — 250,000 токенов — 196 руб.",
            callback_data="buy:14days"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="21 день — 500,000 токенов — 289 руб.",
            callback_data="buy:21days"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="30 дней — 1,000,000 токенов — 597 руб.",
            callback_data="buy:30days_1m"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="30 дней — 5,000,000 токенов — 2790 руб.",
            callback_data="buy:30days_5m"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔥 Безлимит на 1 день",
            callback_data="buy:unlimited_1day"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔹 Купить вечные токены",
            callback_data="eternal_tokens"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔢 Активировать промокод",
            callback_data="activate_promocode"
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
    )

    return builder.as_markup()


def eternal_tokens_keyboard() -> InlineKeyboardMarkup:
    """Eternal tokens selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="150,000 токенов — 149 руб.",
            callback_data="buy:eternal_150k"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="250,000 токенов — 279 руб.",
            callback_data="buy:eternal_250k"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="500,000 токенов — 519 руб.",
            callback_data="buy:eternal_500k"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="1,000,000 токенов — 999 руб.",
            callback_data="buy:eternal_1m"
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="subscription")
    )

    return builder.as_markup()


def ai_models_keyboard() -> InlineKeyboardMarkup:
    """AI models selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="GPT-4 Omni", callback_data="model:gpt-4"),
        InlineKeyboardButton(text="GPT-4 Mini", callback_data="model:gpt-4-mini")
    )
    builder.row(
        InlineKeyboardButton(text="Claude 3.5", callback_data="model:claude"),
        InlineKeyboardButton(text="Gemini Pro", callback_data="model:gemini")
    )
    builder.row(
        InlineKeyboardButton(text="DeepSeek", callback_data="model:deepseek")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
    )

    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    """Profile keyboard with additional options."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💳 Мои платежи", callback_data="my_payments")
    )
    builder.row(
        InlineKeyboardButton(text="🤝🏼 Партнерство", callback_data="referral")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Помощь", callback_data="help")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="main_menu")
    )

    return builder.as_markup()
