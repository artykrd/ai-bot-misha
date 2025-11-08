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


@router.callback_query(F.data.in_(["main_menu", "bot.back"]))
async def show_main_menu(callback: CallbackQuery, user: User):
    """Show main menu. Handles both legacy 'main_menu' and new 'bot.back' callbacks."""
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_user_total_tokens(user.id)

    welcome_text = f"""👋🏻 **Привет!** У тебя на балансе **{total_tokens:,} токенов** ** **– используй их для запросов к нейросетям.

💬 **Языковые модели:**
– **ChatGPT:** работает с текстом, голосом, может принимать до 10 картинок и документы любого формата;
– **Claude** и **Gemini:** отлично работают с текстом и документами;
– **DeepSeek:** отличная альтернатива для сложных задач;
– **Sonar:** модели с доступом к поиску в интернете.

🌄 **Создание изображений:**
– **Midjourney, DALL·E, Stable Diffusion, Recraft** – генерация изображений по описанию;
– **Nano Banana** – создаёт фото по промпту и вашим изображениям;
– **GPT Image** – генерация от OpenAI.

🎬 **Создание видео:**
– **Sora 2, Veo 3.1** – новейшие модели видеогенерации;
– **Midjourney Video, Hailuo, Luma, Kling** – создание видео по описанию.

🎙 **Работа с аудио:**
– **Suno** – создание музыки и песен;
– **Whisper** – расшифровка голосовых сообщений;
– **TTS** – озвучка текста."""

    await callback.message.edit_text(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
