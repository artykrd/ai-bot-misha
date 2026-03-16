#!/usr/bin/env python3
# coding: utf-8

"""
Suno music generation handlers with step-by-step creation.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
import html
import os
import time

from app.bot.keyboards.inline import (
    suno_main_keyboard,
    suno_settings_keyboard,
    suno_version_keyboard,
    suno_type_keyboard,
    suno_style_keyboard,
    suno_lyrics_choice_keyboard,
    suno_back_keyboard,
    suno_final_keyboard,
    suno_vocal_keyboard,
)
from app.bot.states.media import SunoState
from app.bot.states.media import clear_state_preserve_settings
from app.database.models.user import User
from app.database.database import async_session_maker
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.services.audio import SunoService
from app.services.subscription.subscription_service import SubscriptionService
from app.services.ai.openai_service import OpenAIService  # For generating lyrics
from app.services.logging import log_ai_operation_background

logger = get_logger(__name__)

router = Router(name="suno")


# Default Suno settings
DEFAULT_SUNO_SETTINGS = {
    "model_version": "V5",
    "is_instrumental": False,
    "style": "техно, хип-хоп",
    "tokens_per_song": 17600,
}

# Model version display names (API value -> Display name)
MODEL_VERSION_DISPLAY = {
    "V5": "V5",
    "V4_5PLUS": "V4.5 Plus",
    "V4_5ALL": "V4.5 All",
    "V4_5": "V4.5",
    "V4": "V4",
}


def get_version_display_name(version: str) -> str:
    """Get human-readable display name for model version."""
    return MODEL_VERSION_DISPLAY.get(version, version)


async def get_suno_settings(state: FSMContext) -> dict:
    """Get Suno settings from state or return defaults."""
    data = await state.get_data()
    return {
        "model_version": data.get("suno_model_version", DEFAULT_SUNO_SETTINGS["model_version"]),
        "is_instrumental": data.get("suno_is_instrumental", DEFAULT_SUNO_SETTINGS["is_instrumental"]),
        "style": data.get("suno_style", DEFAULT_SUNO_SETTINGS["style"]),
        "tokens_per_song": DEFAULT_SUNO_SETTINGS["tokens_per_song"],
    }


async def calculate_balance_songs(user_id: int, tokens_per_song: int) -> int:
    """Calculate how many songs user can create with current balance."""
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        user_tokens = await sub_service.get_available_tokens(user_id)
    return user_tokens // tokens_per_song


async def show_suno_final_summary(callback_or_message, state: FSMContext):
    """Show final summary screen before generation."""
    data = await state.get_data()

    # Get all parameters
    song_title = data.get("suno_song_title", "Без названия")
    lyrics = data.get("suno_lyrics", None)
    style = data.get("suno_style", DEFAULT_SUNO_SETTINGS["style"])
    model_version = data.get("suno_model_version", DEFAULT_SUNO_SETTINGS["model_version"])
    is_instrumental = data.get("suno_is_instrumental", DEFAULT_SUNO_SETTINGS["is_instrumental"])
    melody_prompt = data.get("suno_melody_prompt", None)
    vocal_gender = data.get("suno_vocal_gender", "m")

    # Escape user input with html.escape for safe HTML rendering
    safe_song_title = html.escape(song_title)
    safe_style = html.escape(style)

    # Determine type and voice
    if is_instrumental:
        song_type = "инструментал"
        voice = "—"
    else:
        song_type = "песня"
        voice = "мужской" if vocal_gender == "m" else "женский"

    # Build summary text
    text = f"⚡ <b>Мы готовы к созданию, давайте всё проверим:</b>\n\n"
    text += f"<b>Название:</b> {safe_song_title}\n"
    text += f"<b>Тип:</b> {song_type}\n"
    text += f"<b>Голос:</b> {voice}\n"
    text += f"<b>Стили:</b> {safe_style}\n\n"

    # Add lyrics or melody prompt
    if is_instrumental and melody_prompt:
        safe_melody = html.escape(melody_prompt[:300])
        ellipsis = '...' if len(melody_prompt) > 300 else ''
        text += f"🎹 <b>Описание мелодии:</b>\n{safe_melody}{ellipsis}\n\n"
    elif lyrics:
        safe_lyrics = html.escape(lyrics[:500])
        ellipsis = '...' if len(lyrics) > 500 else ''
        text += f"📜 <b>Текст:</b>\n{safe_lyrics}{ellipsis}\n\n"

    # Show version info
    text += f"📀 Версия модели: {html.escape(get_version_display_name(model_version))}"

    # Send or edit message
    if isinstance(callback_or_message, CallbackQuery):
        try:
            await callback_or_message.message.edit_text(
                text,
                reply_markup=suno_final_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest as e:
            # Ignore error if message content hasn't changed
            if "message is not modified" not in str(e):
                raise
        await callback_or_message.answer()
    else:
        await callback_or_message.answer(
            text,
            reply_markup=suno_final_keyboard(),
            parse_mode=ParseMode.HTML
        )


@router.callback_query(F.data == "bot.suno")
async def start_suno(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Suno music generation."""
    # Preserve user settings before clearing state
    data = await state.get_data()
    saved_settings = {
        "suno_model_version": data.get("suno_model_version"),
        "suno_is_instrumental": data.get("suno_is_instrumental"),
        "suno_style": data.get("suno_style"),
        "suno_selected_styles": data.get("suno_selected_styles"),
    }

    await clear_state_preserve_settings(state)  # Clear song creation state (title, lyrics, etc.)

    # Restore user settings if they were set
    settings_to_restore = {k: v for k, v in saved_settings.items() if v is not None}
    if settings_to_restore:
        await state.update_data(**settings_to_restore)

    settings = await get_suno_settings(state)
    balance_songs = await calculate_balance_songs(user.id, settings["tokens_per_song"])

    type_text = "инструментал (без слов)" if settings["is_instrumental"] else "с текстом песни"

    # Escape user input with html.escape for safe HTML rendering
    safe_style = html.escape(settings['style'])

    text = (
        f"🎧 <b>Suno · создание музыки</b>\n\n"
        f"Вы можете отрегулировать параметры ниже и отправить мне текст песни или создать песню пошагово "
        f"(в этом режиме можно сгенерировать текст через ИИ).\n\n"
        f"В ответ я отправлю вам две песни и обложки к ним.\n\n"
        f"⚙️ <b>Параметры</b>\n"
        f"Версия: {html.escape(get_version_display_name(settings['model_version']))}\n"
        f"Тип: {html.escape(type_text)}\n"
        f"Стиль: {safe_style}\n\n"
        f"🔹 <b>Баланса хватит на {balance_songs} песен.</b> 1 генерация = {settings['tokens_per_song']:,} токенов"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=suno_main_keyboard(
                model_version=settings["model_version"],
                is_instrumental=settings["is_instrumental"],
                style=settings["style"],
                balance_songs=balance_songs,
                tokens_per_song=settings["tokens_per_song"]
            ),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


# ======================
# SETTINGS HANDLERS
# ======================

@router.callback_query(F.data == "suno.settings")
async def suno_settings(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Suno settings menu."""
    settings = await get_suno_settings(state)
    type_text = "инструментал (без слов)" if settings["is_instrumental"] else "с текстом песни"

    # Escape user input with html.escape for safe HTML rendering
    safe_style = html.escape(settings['style'])

    text = (
        f"⚙️ <b>Параметры Suno</b>\n\n"
        f"📀 Версия: <b>{html.escape(get_version_display_name(settings['model_version']))}</b>\n"
        f"🎵 Тип: <b>{html.escape(type_text)}</b>\n"
        f"🎨 Стиль: <b>{safe_style}</b>"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=suno_settings_keyboard(
                model_version=settings["model_version"],
                is_instrumental=settings["is_instrumental"],
                style=settings["style"]
            ),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "suno.change_version")
async def suno_change_version(callback: CallbackQuery, state: FSMContext):
    """Show version selection menu."""
    text = (
        "📀 <b>Выберите версию модели</b>\n\n"
        "• <b>V5</b> - лучшее музыкальное выражение, быстрая генерация\n"
        "• <b>V4.5 Plus</b> - более богатый звук, новые способы создания, до 8 минут\n"
        "• <b>V4.5 All</b> - лучшая структура песни, до 8 минут\n"
        "• <b>V4.5</b> - умные промпты, быстрая генерация, до 8 минут\n"
        "• <b>V4</b> - улучшенное качество вокала, до 4 минут"
    )

    try:
        await callback.message.edit_text(text, reply_markup=suno_version_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("suno.set_version_"))
async def suno_set_version(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Suno model version."""
    version = callback.data.replace("suno.set_version_", "")
    await state.update_data(suno_model_version=version)

    await callback.answer(f"✅ Версия изменена на {get_version_display_name(version)}")
    await suno_settings(callback, state, user)


@router.callback_query(F.data == "suno.change_type")
async def suno_change_type(callback: CallbackQuery, state: FSMContext):
    """Show type selection menu."""
    text = (
        "🎵 <b>Выберите тип песни</b>\n\n"
        "• <b>С текстом песни</b> - будет использоваться вокал и текст\n"
        "• <b>Инструментал (без слов)</b> - только музыка без вокала"
    )

    try:
        await callback.message.edit_text(text, reply_markup=suno_type_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "suno.set_type_lyrics")
async def suno_set_type_lyrics(callback: CallbackQuery, state: FSMContext, user: User):
    """Set type to with lyrics."""
    await state.update_data(suno_is_instrumental=False)
    await callback.answer("✅ Тип изменен на 'с текстом песни'")
    await suno_settings(callback, state, user)


@router.callback_query(F.data == "suno.set_type_instrumental")
async def suno_set_type_instrumental(callback: CallbackQuery, state: FSMContext, user: User):
    """Set type to instrumental."""
    await state.update_data(suno_is_instrumental=True)
    await callback.answer("✅ Тип изменен на 'инструментал'")
    await suno_settings(callback, state, user)


@router.callback_query(F.data == "suno.change_style")
async def suno_change_style(callback: CallbackQuery, state: FSMContext):
    """Show style selection menu."""
    data = await state.get_data()
    selected_styles = data.get("suno_selected_styles", [])

    text = (
        "🎨 <b>Выберите стили музыки</b>\n\n"
        "Вы можете выбрать до 3 стилей одновременно.\n"
        "После выбора нажмите \"👍 Я выбрал(а) стили\"."
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=suno_style_keyboard(selected_styles),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("suno.toggle_style_"))
async def suno_toggle_style(callback: CallbackQuery, state: FSMContext):
    """Toggle style selection (add or remove from list)."""
    style = callback.data.replace("suno.toggle_style_", "")
    data = await state.get_data()
    selected_styles = data.get("suno_selected_styles", [])

    if style in selected_styles:
        # Remove style
        selected_styles.remove(style)
    else:
        # Add style (max 3)
        if len(selected_styles) < 3:
            selected_styles.append(style)
        else:
            await callback.answer("⚠️ Максимум 3 стиля!", show_alert=True)
            return

    await state.update_data(suno_selected_styles=selected_styles)

    # Update keyboard
    text = (
        "🎨 <b>Выберите стили музыки</b>\n\n"
        "Вы можете выбрать до 3 стилей одновременно.\n"
        "После выбора нажмите \"👍 Я выбрал(а) стили\"."
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=suno_style_keyboard(selected_styles),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "suno.confirm_styles")
async def suno_confirm_styles(callback: CallbackQuery, state: FSMContext):
    """Confirm selected styles and save."""
    data = await state.get_data()
    selected_styles = data.get("suno_selected_styles", [])

    if not selected_styles:
        await callback.answer("⚠️ Выберите хотя бы один стиль!", show_alert=True)
        return

    # Combine styles into comma-separated string
    style_string = ", ".join(selected_styles)
    await state.update_data(suno_style=style_string)

    await callback.answer(f"✅ Выбрано стилей: {len(selected_styles)}")

    # Check if instrumental - skip vocal selection for instrumental
    is_instrumental = data.get("suno_is_instrumental", False)
    if is_instrumental:
        # Show final summary screen directly
        await show_suno_final_summary(callback, state)
    else:
        # Show vocal selection screen for songs with lyrics
        text = (
            "3️⃣ <b>Выберите тип вокала</b>\n\n"
            "Выберите, каким голосом будет исполнена песня:"
        )
        try:
            await callback.message.edit_text(
                text,
                reply_markup=suno_vocal_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest as e:
            # Ignore error if message content hasn't changed
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


# ======================
# VOCAL SELECTION
# ======================

@router.callback_query(F.data.startswith("suno.set_vocal_"))
async def suno_set_vocal(callback: CallbackQuery, state: FSMContext):
    """Toggle vocal type selection."""
    vocal_type = callback.data.replace("suno.set_vocal_", "")

    # Store selected vocal in state
    await state.update_data(suno_vocal_gender=vocal_type)

    # Update keyboard to show new selection
    text = (
        "3️⃣ <b>Выберите тип вокала</b>\n\n"
        "Выберите, каким голосом будет исполнена песня:"
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=suno_vocal_keyboard(selected_vocal=vocal_type),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "suno.confirm_vocal")
async def suno_confirm_vocal(callback: CallbackQuery, state: FSMContext):
    """Confirm vocal selection and show final summary."""
    data = await state.get_data()
    vocal_gender = data.get("suno_vocal_gender", "m")  # Default to male

    # Ensure vocal is stored
    await state.update_data(suno_vocal_gender=vocal_gender)

    await callback.answer("✅ Тип вокала сохранен")

    # Show final summary screen
    await show_suno_final_summary(callback, state)


# ======================
# STYLE SELECTION (LEGACY)
# ======================

@router.callback_query(F.data.startswith("suno.set_style_"))
async def suno_set_style(callback: CallbackQuery, state: FSMContext, user: User):
    """Legacy single style selection - proceed to vocal selection or final summary."""
    style = callback.data.replace("suno.set_style_", "")
    await state.update_data(suno_selected_styles=[style], suno_style=style)

    # Check if instrumental - skip vocal selection for instrumental
    data = await state.get_data()
    is_instrumental = data.get("suno_is_instrumental", False)

    if is_instrumental:
        # Show final summary screen directly
        await show_suno_final_summary(callback, state)
    else:
        # Show vocal selection screen for songs with lyrics
        text = (
            "3️⃣ <b>Выберите тип вокала</b>\n\n"
            "Выберите, каким голосом будет исполнена песня:"
        )
        try:
            await callback.message.edit_text(
                text,
                reply_markup=suno_vocal_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest as e:
            # Ignore error if message content hasn't changed
            if "message is not modified" not in str(e):
                raise
        await callback.answer()


@router.callback_query(F.data == "suno.custom_style")
async def suno_custom_style(callback: CallbackQuery, state: FSMContext):
    """Ask user to input custom style."""
    text = (
        "✏️ <b>Введите свой стиль музыки</b>\n\n"
        "Напишите стиль в свободной форме, например:\n"
        "• электронная музыка с элементами ambient\n"
        "• акустическая баллада\n"
        "• агрессивный металкор\n"
        "• летний поп с тропическими мотивами"
    )

    await state.set_state(SunoState.waiting_for_style)
    try:
        await callback.message.edit_text(text, reply_markup=suno_back_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(SunoState.waiting_for_style, F.text)
async def process_custom_style(message: Message, state: FSMContext, user: User):
    """Process custom style input and proceed to vocal selection or final summary."""
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return
    style = message.text.strip()
    await state.update_data(suno_style=style, suno_selected_styles=[style])

    # Check if instrumental - skip vocal selection for instrumental
    data = await state.get_data()
    is_instrumental = data.get("suno_is_instrumental", False)

    if is_instrumental:
        # Show final summary screen directly
        await show_suno_final_summary(message, state)
    else:
        # Show vocal selection screen for songs with lyrics
        text = (
            "3️⃣ <b>Выберите тип вокала</b>\n\n"
            "Выберите, каким голосом будет исполнена песня:"
        )
        await message.answer(
            text,
            reply_markup=suno_vocal_keyboard(),
            parse_mode=ParseMode.HTML
        )


# ======================
# STEP-BY-STEP CREATION
# ======================

@router.callback_query(F.data == "suno.step_by_step")
async def suno_step_by_step(callback: CallbackQuery, state: FSMContext):
    """Start step-by-step song creation."""
    text = (
        "1️⃣ <b>Введите название новой песни</b>\n\n"
        "Например: я люблю тебя, жизнь"
    )

    await state.set_state(SunoState.waiting_for_song_title)
    try:
        await callback.message.edit_text(text, reply_markup=suno_back_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(SunoState.waiting_for_song_title, F.text)
async def process_song_title(message: Message, state: FSMContext):
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return
    """Process song title and ask for lyrics choice."""
    song_title = message.text.strip()
    await state.update_data(suno_song_title=song_title)

    # Escape user input with html.escape for safe HTML rendering
    safe_song_title = html.escape(song_title)

    text = (
        f"2️⃣ <b>Введите текст песни</b>\n\n"
        f"⚡️ При написании текста самостоятельно можно использовать все доступные теги для Suno.\n\n"
        f"🤖 <b>Помощь с написанием текста:</b>\n"
        f"– <b>По названию</b>: ИИ напишет текст песни по названию «{safe_song_title}»;\n"
        f"– <b>По описанию</b>: ИИ напишет текст песни по вашему короткому рассказу.\n\n"
        f"⚙️ <b>Дополнительно:</b>\n"
        f"– <b>Создать без слов</b>: вы сможете управлять мелодией с помощью промпта или сразу перейти к выбору стиля."
    )

    await message.answer(text, reply_markup=suno_lyrics_choice_keyboard(song_title), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "suno.lyrics_by_title")
async def suno_lyrics_by_title(callback: CallbackQuery, state: FSMContext, user: User):
    """Generate lyrics by title using AI."""
    data = await state.get_data()
    song_title = data.get("suno_song_title", "Untitled")

    progress_msg = await callback.message.edit_text("🤖 Генерирую текст песни по названию...")

    try:
        # Use GPT to generate lyrics
        openai_service = OpenAIService()
        prompt = f"Напиши текст песни с названием '{song_title}'. Используй структуру [Intro], [Verse], [Chorus], [Bridge], [Outro]. Текст должен быть эмоциональным и запоминающимся."

        response = await openai_service.generate_text(
            prompt=prompt,
            model="gpt-4o-mini",
            max_tokens=1000
        )

        # Extract text from AIResponse object
        if not response.success or not response.content:
            raise ValueError(response.error or "Не удалось сгенерировать текст")

        lyrics = response.content

        await state.update_data(suno_lyrics=lyrics)

        text = (
            f"✅ **Текст песни сгенерирован!**\n\n"
            f"{lyrics[:500]}{'...' if len(lyrics) > 500 else ''}\n\n"
            f"Теперь выберите стиль или начните генерацию."
        )

        data = await state.get_data()
        selected_styles = data.get("suno_selected_styles", [])
        await progress_msg.edit_text(text, reply_markup=suno_style_keyboard(selected_styles), parse_mode=None)

    except Exception as e:
        from app.core.error_handlers import format_user_error
        logger.error("suno_lyrics_generation_failed", error=str(e))
        user_message = format_user_error(e, provider="Suno")
        await progress_msg.edit_text(
            f"❌ {user_message}\n\nПопробуйте ввести текст вручную.",
            reply_markup=suno_lyrics_choice_keyboard(song_title),
            parse_mode=None
        )


@router.callback_query(F.data == "suno.lyrics_by_description")
async def suno_lyrics_by_description(callback: CallbackQuery, state: FSMContext):
    """Ask for song description to generate lyrics."""
    text = (
        "💬 <b>Расскажите мне о песне</b>\n\n"
        "Возможно, вы хотите сделать подарок близкому человеку или удивить коллег. "
        "Напишите сюжет своей песни, а я помогу составить для неё текст.\n\n"
        "📌 <b>Примеры запросов:</b>\n"
        "- Напиши песню для моей любимой мамы, ... (расскажи небольшую историю о ней и подчеркни моменты, которые хотите услышать в песне);\n"
        "- Танцевальный трек про лето, с легким припевом и незамысловатым текстом.\n\n"
        "🔹 <b>Создание текста стоит 1,000 токенов</b>"
    )

    await state.set_state(SunoState.waiting_for_lyrics_description)
    try:
        await callback.message.edit_text(text, reply_markup=suno_back_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(SunoState.waiting_for_lyrics_description, F.text)
async def process_lyrics_description(message: Message, state: FSMContext, user: User):
    """Generate lyrics from description."""
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return

    description = message.text.strip()

    # Check tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, 1000)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для генерации текста!\n\n"
                f"Требуется: 1,000 токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            return

    progress_msg = await message.answer("🤖 Генерирую текст песни по описанию...")

    try:
        openai_service = OpenAIService()
        data = await state.get_data()
        song_title = data.get("suno_song_title", "")

        prompt = f"Напиши текст песни на основе следующего описания: {description}\n"
        if song_title:
            prompt += f"\nНазвание песни: {song_title}\n"
        prompt += "Используй структуру [Intro], [Verse], [Chorus], [Bridge], [Outro]. Текст должен быть эмоциональным и соответствовать описанию."

        response = await openai_service.generate_text(
            prompt=prompt,
            model="gpt-4o-mini",
            max_tokens=1000
        )

        # Extract text from AIResponse object
        if not response.success or not response.content:
            raise ValueError(response.error or "Не удалось сгенерировать текст")

        lyrics = response.content

        await state.update_data(suno_lyrics=lyrics)

        text = (
            f"✅ **Текст песни сгенерирован!**\n\n"
            f"{lyrics[:500]}{'...' if len(lyrics) > 500 else ''}\n\n"
            f"Теперь выберите стиль или начните генерацию."
        )

        data = await state.get_data()
        selected_styles = data.get("suno_selected_styles", [])
        await progress_msg.edit_text(text, reply_markup=suno_style_keyboard(selected_styles), parse_mode=None)

    except Exception as e:
        from app.core.error_handlers import format_user_error
        logger.error("suno_lyrics_generation_failed", error=str(e))
        user_message = format_user_error(e, provider="Suno")
        await progress_msg.edit_text(
            f"❌ {user_message}\n\nПопробуйте ввести текст вручную.",
            parse_mode=None
        )


@router.callback_query(F.data == "suno.lyrics_custom")
async def suno_lyrics_custom(callback: CallbackQuery, state: FSMContext):
    """Ask user to input custom lyrics."""
    text = (
        "✏️ <b>Введите текст песни</b>\n\n"
        "Вы можете использовать специальные теги Suno для структуры песни:\n"
        "• [Intro] - вступление\n"
        "• [Verse] - куплет\n"
        "• [Chorus] - припев\n"
        "• [Bridge] - бридж\n"
        "• [Outro] - концовка\n\n"
        "Просто напишите текст, и я создам из него песню!"
    )

    await state.set_state(SunoState.waiting_for_lyrics_text)
    try:
        await callback.message.edit_text(text, reply_markup=suno_back_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(SunoState.waiting_for_lyrics_text, F.text)
async def process_custom_lyrics(message: Message, state: FSMContext):
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return
    """Process custom lyrics input."""
    lyrics = message.text.strip()
    await state.update_data(suno_lyrics=lyrics)

    data = await state.get_data()
    selected_styles = data.get("suno_selected_styles", [])

    await message.answer(
        f"✅ Текст сохранен! Теперь выберите стиль:",
        reply_markup=suno_style_keyboard(selected_styles)
    )


@router.callback_query(F.data == "suno.lyrics_instrumental")
async def suno_lyrics_instrumental(callback: CallbackQuery, state: FSMContext):
    """Create instrumental song - ask for melody prompt."""
    text = (
        "🎶 <b>Мы генерируем песню без слов: желаете как-нибудь поуправлять мелодией?</b>\n\n"
        "Достаточного простого описания или полного с указанием основных тегов.\n\n"
        "📌 <b>Примеры управления мелодией:</b>\n"
        "- EDM-поп инструментал, 100 BPM, синт-пиано и саб-бас, чистый звук, структура: 0–20 вступление, 20–40 развёртка, 40–60 финал;\n"
        "- Альтернатива-рок трек, гитара riffs, электрогитары, барабаны, динамика нарастает к концу, 90 BPM;\n"
        "- Ambient/роко-инструментал, медленный темп 70 BPM, просторный синт, плавные переходы, без резких качков;\n\n"
        "ℹ️ Можете пропустить этот шаг и перейдем сразу к выбору стиля."
    )

    await state.update_data(suno_is_instrumental=True, suno_lyrics=None)
    await state.set_state(SunoState.waiting_for_melody_prompt)
    try:
        await callback.message.edit_text(text, reply_markup=suno_style_keyboard(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest as e:
        # Ignore error if message content hasn't changed
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(SunoState.waiting_for_melody_prompt, F.text)
async def process_melody_prompt(message: Message, state: FSMContext):
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return
    """Process melody prompt for instrumental."""
    melody_prompt = message.text.strip()
    await state.update_data(suno_melody_prompt=melody_prompt)

    data = await state.get_data()
    selected_styles = data.get("suno_selected_styles", [])

    await message.answer(
        f"✅ Описание мелодии сохранено! Теперь выберите стиль:",
        reply_markup=suno_style_keyboard(selected_styles)
    )


# ======================
# SONG GENERATION
# ======================

@router.callback_query(F.data == "suno.generate_song")
async def generate_suno_song(callback: CallbackQuery, state: FSMContext, user: User):
    """Generate song with Suno AI."""
    data = await state.get_data()

    # Get all required parameters
    song_title = data.get("suno_song_title", "Untitled")
    lyrics = data.get("suno_lyrics", None)
    style = data.get("suno_style", DEFAULT_SUNO_SETTINGS["style"])
    model_version = data.get("suno_model_version", DEFAULT_SUNO_SETTINGS["model_version"])
    is_instrumental = data.get("suno_is_instrumental", DEFAULT_SUNO_SETTINGS["is_instrumental"])
    melody_prompt = data.get("suno_melody_prompt", None)
    vocal_gender = data.get("suno_vocal_gender", "m")  # Default to male

    # Validate required data
    if not is_instrumental and not lyrics:
        await callback.answer("❌ Не указан текст песни!", show_alert=True)
        return

    # Check tokens
    tokens_cost = DEFAULT_SUNO_SETTINGS["tokens_per_song"]
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, tokens_cost)
        except InsufficientTokensError as e:
            await callback.answer(
                f"❌ Недостаточно токенов!\n\nТребуется: {tokens_cost:,}\nДоступно: {e.details['available']:,}",
                show_alert=True
            )
            return

    # Answer callback immediately to prevent "query is too old" error
    # Generation takes ~2 minutes, but Telegram requires answer within 30 seconds
    await callback.answer()

    progress_msg = await callback.message.edit_text("🎵 Генерирую песню... Это может занять 1-2 минуты.")

    # Track generation time for logging
    generation_start_time = time.time()

    try:
        suno_service = SunoService()

        # Prepare generation parameters
        # prompt is REQUIRED - it's either melody description or song lyrics
        if is_instrumental and melody_prompt:
            prompt = melody_prompt
            instrumental = True
        elif lyrics:
            prompt = lyrics  # lyrics are the prompt for non-instrumental
            instrumental = False
        else:
            # Fallback: create prompt from title and style
            prompt = f"{song_title} in {style} style"
            instrumental = is_instrumental

        generation_params = {
            "prompt": prompt,
            "title": song_title,
            "style": style,
            "instrumental": instrumental,
            "model": model_version.replace(".", "_").replace(" ", "_"),
        }

        # Add vocal gender for non-instrumental songs
        if not instrumental:
            generation_params["vocalGender"] = vocal_gender

        # Generate song
        result = await suno_service.generate_audio(**generation_params)

        if result.success:
            await progress_msg.edit_text(
                f"✅ **Песня создана!**\n\n"
                f"🎵 Название: {song_title}\n"
                f"🎨 Стиль: {style}\n"
                f"📀 Версия: {get_version_display_name(model_version)}\n\n"
                f"Отправляю файлы...",
                parse_mode=None
            )

            # Send audio file(s)
            if result.audio_path:
                await callback.message.answer_audio(
                    audio=FSInputFile(result.audio_path),
                    title=song_title,
                    performer="Suno AI"
                )

            # Send cover image if available
            if result.image_path and os.path.exists(result.image_path):
                await callback.message.answer_photo(photo=FSInputFile(result.image_path))

            await progress_msg.delete()
            await clear_state_preserve_settings(state)

            logger.info(
                "suno_song_generated",
                user_id=user.id,
                title=song_title,
                style=style,
                model_version=model_version,
                is_instrumental=is_instrumental,
                tokens=tokens_cost
            )

            # Log AI operation for cost tracking (fire-and-forget)
            elapsed_time = int(time.time() - generation_start_time)
            log_ai_operation_background(
                user_id=user.id,
                model_id="suno",
                operation_category="audio_gen",
                tokens_cost=tokens_cost,
                prompt=f"{song_title}: {style}"[:500],
                status="completed",
                response_file_path=result.audio_path,
                processing_time_seconds=elapsed_time,
                input_data={
                    "model_version": model_version,
                    "is_instrumental": is_instrumental,
                    "style": style,
                    "vocal_gender": vocal_gender if not is_instrumental else None,
                },
            )
        else:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации: {result.error}\n\n"
                f"Токены возвращены на ваш счет."
            )

            # Refund tokens via rollback (creates refund subscription to avoid wrong-sub bug)
            async with async_session_maker() as session:
                sub_service = SubscriptionService(session)
                await sub_service.rollback_tokens(user.id, tokens_cost)
                logger.info("tokens_refunded", user_id=user.id, amount=tokens_cost)

            logger.error(
                "suno_generation_failed",
                user_id=user.id,
                error=result.error
            )

            # Log failed AI operation for tracking
            elapsed_time = int(time.time() - generation_start_time)
            log_ai_operation_background(
                user_id=user.id,
                model_id="suno",
                operation_category="audio_gen",
                tokens_cost=0,  # Tokens were refunded
                prompt=f"{song_title}: {style}"[:500],
                status="failed",
                error_message=str(result.error)[:500],
                processing_time_seconds=elapsed_time,
                input_data={
                    "model_version": model_version,
                    "is_instrumental": is_instrumental,
                    "style": style,
                },
            )

    except Exception as e:
        from app.core.error_handlers import format_user_error
        logger.error("suno_generation_exception", user_id=user.id, error=str(e))
        user_message = format_user_error(e, provider="Suno", user_id=user.id)
        await progress_msg.edit_text(
            f"❌ {user_message}\n\n"
            f"Токены возвращены на ваш счет.",
            parse_mode=None
        )

        # Refund tokens via rollback (creates refund subscription to avoid wrong-sub bug)
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.rollback_tokens(user.id, tokens_cost)
            logger.info("tokens_refunded", user_id=user.id, amount=tokens_cost)

        # Log failed AI operation for tracking
        elapsed_time = int(time.time() - generation_start_time)
        log_ai_operation_background(
            user_id=user.id,
            model_id="suno",
            operation_category="audio_gen",
            tokens_cost=0,  # Tokens were refunded
            prompt=f"{song_title}: {style}"[:500],
            status="failed",
            error_message=str(e)[:500],
            processing_time_seconds=elapsed_time,
            input_data={
                "model_version": model_version,
                "is_instrumental": is_instrumental,
                "style": style,
            },
        )
