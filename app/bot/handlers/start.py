"""
Start command handler.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.inline import main_menu_keyboard
from app.database.models.user import User

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: User):
    """Handle /start command."""

    total_tokens = user.get_total_tokens()

    welcome_text = f"""👋🏻 **Привет!** У тебя на балансе **{total_tokens:,} токенов** – используй их для запросов к нейросетям.

💬 **Языковые модели:**
– **ChatGPT:** работает с текстом, голосом, может принимать до 10 картинок и анализировать их;
– **Claude, Gemini, DeepSeek** и другие модели для диалога.

🌄 **Генерация изображений:**
– **Nano Banana, Midjourney, DALL-E 3, Stable Diffusion** и другие.

🎞 **Генерация видео:**
– **Sora, Veo, Luma, Kling** и другие.

🎙 **Аудио:**
– **Suno** для создания музыки;
– **Whisper** для распознавания речи;
– **TTS** для озвучки текста.

✂️ **Инструменты:**
– Улучшение качества, удаление фона, векторизация и многое другое.

Выбери нужный раздел в меню ниже! 👇"""

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, user: User):
    """Show main menu."""

    total_tokens = user.get_total_tokens()

    welcome_text = f"""👋🏻 **Главное меню**

💰 Баланс: **{total_tokens:,} токенов**

Выбери нужный раздел ниже! 👇"""

    await callback.message.edit_text(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
