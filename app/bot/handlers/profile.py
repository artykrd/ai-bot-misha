"""
Profile handler.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

from app.bot.keyboards.inline import profile_keyboard
from app.database.models.user import User
from app.database.database import async_session_maker
from app.services.subscription.subscription_service import SubscriptionService

router = Router(name="profile")


# Token costs for different services
TOKEN_COSTS = {
    "gpt-4-mini": 500,
    "gpt-4-mini-vision": 3000,
    "nano-banana": 8000,
    "gpt-image": 8000,
    "midjourney": 20000,
    "dalle": 10000,
    "stable-diffusion": 15000,
    "recraft": 15000,
    "faceswap": 8000,
    "photo-enhance": 2000,
    "bg-replace": 15000,
    "bg-remove": 8000,
    "vectorize": 8000,
    "sora": 50000,
    "veo": 50000,
    "mj-video": 30000,
    "hailuo": 30000,
    "luma": 30000,
    "kling": 30000,
    "kling-effects": 30000,
    "suno": 20000,
    "whisper-per-min": 1000,
    "tts-per-1k-chars": 1,
}


def calculate_service_availability(total_tokens: int) -> str:
    """Calculate what services are available with current token balance."""
    lines = []

    if total_tokens >= TOKEN_COSTS["gpt-4-mini"]:
        count = total_tokens // TOKEN_COSTS["gpt-4-mini"]
        lines.append(f"- {count} запросов к ChatGPT 4 Omni Mini;")

    if total_tokens >= TOKEN_COSTS["gpt-4-mini-vision"]:
        count = total_tokens // TOKEN_COSTS["gpt-4-mini-vision"]
        lines.append(f"- {count} запросов к ChatGPT Omni Mini с обработкой фотографий;")

    if total_tokens >= TOKEN_COSTS["nano-banana"]:
        count = total_tokens // TOKEN_COSTS["nano-banana"]
        lines.append(f"- Nano Banana: {count} запроса;")

    if total_tokens >= TOKEN_COSTS["gpt-image"]:
        count = total_tokens // TOKEN_COSTS["gpt-image"]
        lines.append(f"- GPT Image 1: {count} запроса;")

    count = total_tokens // TOKEN_COSTS["midjourney"]
    lines.append(f"- Midjourney: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["dalle"]
    lines.append(f"- DALL·E: {count} запрос{'ов' if count != 1 else ''};")

    count = total_tokens // TOKEN_COSTS["stable-diffusion"]
    lines.append(f"- Stable Diffusion: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["recraft"]
    lines.append(f"- Recraft: {count} запросов;")

    if total_tokens >= TOKEN_COSTS["faceswap"]:
        count = total_tokens // TOKEN_COSTS["faceswap"]
        lines.append(f"- Замена лиц: {count} запроса для замены лиц;")

    if total_tokens >= TOKEN_COSTS["photo-enhance"]:
        count = total_tokens // TOKEN_COSTS["photo-enhance"]
        lines.append(f"- Улучшение фото: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["bg-replace"]
    lines.append(f"- Замена фона: {count} запросов;")

    if total_tokens >= TOKEN_COSTS["bg-remove"]:
        count = total_tokens // TOKEN_COSTS["bg-remove"]
        lines.append(f"- Удаление фона: {count} запроса;")

    if total_tokens >= TOKEN_COSTS["vectorize"]:
        count = total_tokens // TOKEN_COSTS["vectorize"]
        lines.append(f"- Векторизация фото: {count} запроса;")

    count = total_tokens // TOKEN_COSTS["sora"]
    lines.append(f"- Sora 2: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["veo"]
    lines.append(f"- Veo 3.1: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["mj-video"]
    lines.append(f"- Midjourney Video: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["hailuo"]
    lines.append(f"- Hailuo: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["luma"]
    lines.append(f"- Luma Dream Machine: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["kling"]
    lines.append(f"- Kling: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["kling-effects"]
    lines.append(f"- Kling Effects: {count} запросов;")

    count = total_tokens // TOKEN_COSTS["suno"]
    lines.append(f"- Создание песен: {count} запросов (Suno);")

    minutes = total_tokens // TOKEN_COSTS["whisper-per-min"]
    lines.append(f"- {minutes} минут расшифровки аудио;")

    chars = total_tokens // TOKEN_COSTS["tts-per-1k-chars"] * 1000
    lines.append(f"- {chars:,} символов перевода текста в голос.")

    return "\n".join(lines)


@router.callback_query(F.data == "profile")
@router.message(Command("profile"))
async def show_profile(event, user: User):
    """Show user profile with detailed token breakdown."""

    # Handle both callback and message
    is_callback = isinstance(event, CallbackQuery)

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        total_tokens = await sub_service.get_user_total_tokens(user.id)
        # Get total spent tokens (placeholder for now)
        spent_tokens = 0  # TODO: implement tracking

    # Calculate service availability
    services_text = calculate_service_availability(total_tokens)

    # Format profile text in HTML
    profile_text = f"""📊 <b>Мой профиль</b>

🆔 ID: {user.telegram_id}
👤 Имя: {user.full_name}
📨 Имейл: не указан
🔹 Баланс: {total_tokens:,} токенов

ℹ️ На какие сервисы хватит баланса? · примерно
{services_text}

🔸 Потрачено: {spent_tokens:,} токена
- ChatGPT: 0
- DALL·E 3: 0
- Stable Diffusion: 0
- Midjourney: 0"""

    if is_callback:
        await event.message.edit_text(
            profile_text,
            reply_markup=profile_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await event.answer()
    else:
        await event.answer(
            profile_text,
            reply_markup=profile_keyboard(),
            parse_mode=ParseMode.HTML
        )
