#!/usr/bin/env python3
# coding: utf-8

"""
Media handlers for video, audio, and image generation.
"""

import asyncio

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
import os
from pathlib import Path
from PIL import Image
import io

from app.bot.keyboards.inline import (
    back_to_main_keyboard,
    kling_choice_keyboard,
    kling_main_keyboard,
    kling_settings_keyboard,
    kling_aspect_ratio_keyboard,
    kling_duration_keyboard,
    kling_version_keyboard,
    kling_auto_translate_keyboard,
    kling_image_main_keyboard,
    kling_image_settings_keyboard,
    kling_image_aspect_ratio_keyboard,
    kling_image_model_keyboard,
    kling_image_resolution_keyboard,
    kling_image_auto_translate_keyboard,
    kling_effects_main_keyboard,
    kling_effects_categories_keyboard,
    kling_effects_list_keyboard,
    kling_effects_confirm_keyboard,
    nano_banana_keyboard,
    nano_format_keyboard,
    nano_multi_images_keyboard,
    seedream_keyboard,
    seedream_size_keyboard,
    seedream_batch_count_keyboard,
    seedream_back_keyboard,
    kling_motion_control_keyboard,
    kling_mc_settings_keyboard,
    kling_mc_mode_keyboard,
    kling_mc_orientation_keyboard,
    kling_mc_sound_keyboard,
)
from app.bot.states import MediaState
from app.bot.states.media import KlingSettings, KlingImageSettings
from app.bot.utils.notifications import (
    format_generation_message,
    create_action_keyboard,
    CONTENT_TYPES,
    MODEL_ACTIONS,
)
from app.database.models.user import User
from app.database.database import async_session_maker
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.core.cost_guard import cost_guard
from app.core.billing_config import (
    get_image_model_billing,
    get_video_model_billing,
    format_token_amount,
    get_kling_tokens_cost,
    get_kling_api_model,
)
from app.core.temp_files import get_temp_file_path, cleanup_temp_file
from app.services.video import VeoService, SoraService, LumaService, HailuoService, KlingService
from app.services.video.kling_effects_service import KlingEffectsService
from app.services.image import DalleService, GeminiImageService, StabilityService, RemoveBgService, NanoBananaService, KlingImageService, RecraftService, SeedreamService, MidjourneyService
from app.services.audio import SunoService, OpenAIAudioService
from app.services.ai.vision_service import VisionService
from app.services.subscription.subscription_service import SubscriptionService

logger = get_logger(__name__)

router = Router(name="media")


# ======================
# UTILITY FUNCTIONS
# ======================

async def cleanup_temp_images(state: FSMContext):
    """Clean up temporary image files from state."""
    data = await state.get_data()
    for key in ["image_path", "reference_image_path"]:
        file_path = data.get(key)
        if file_path:
            cleanup_temp_file(file_path)


async def get_available_tokens(user_id: int) -> int:
    """Fetch available tokens for user from subscriptions."""
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        return await sub_service.get_available_tokens(user_id)


def resize_image_if_needed(image_path: str, max_size_mb: float = 2.0, max_dimension: int = 2048) -> str:
    """
    Resize image if it's too large.

    Args:
        image_path: Path to the image file
        max_size_mb: Maximum file size in MB
        max_dimension: Maximum width or height in pixels

    Returns:
        Path to the resized image (same as input if no resize needed)
    """
    try:
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)

        img = Image.open(image_path)
        needs_resize = False

        # Check if file size is too large
        if file_size_mb > max_size_mb:
            needs_resize = True
            logger.info("image_too_large", size_mb=file_size_mb)

        # Check if dimensions are too large
        if img.width > max_dimension or img.height > max_dimension:
            needs_resize = True
            logger.info("image_dimensions_too_large", width=img.width, height=img.height)

        if not needs_resize:
            return image_path

        # Calculate new dimensions maintaining aspect ratio
        ratio = min(max_dimension / img.width, max_dimension / img.height, 1.0)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)

        # Convert RGBA to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(
                img,
                mask=img.split()[-1] if img.mode == "RGBA" else None
            )
            img = background

        # Resize image
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save with optimization
        img_resized.save(image_path, "JPEG", quality=85, optimize=True)

        new_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        logger.info(
            "image_resized",
            old_size_mb=file_size_mb,
            new_size_mb=new_size_mb,
            old_dimensions=f"{img.width}x{img.height}",
            new_dimensions=f"{new_width}x{new_height}"
        )

        return image_path

    except Exception as e:
        logger.error("image_resize_failed", error=str(e))
        return image_path


# ======================
# VIDEO SERVICES
# ======================

@router.callback_query(F.data == "bot.veo")
async def start_veo(callback: CallbackQuery, state: FSMContext, user: User):
    # Get user's total tokens
    total_tokens = await get_available_tokens(user.id)
    veo_billing = get_video_model_billing("veo-3.1-fast")
    videos_available = int(total_tokens / veo_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "🌊 **Veo 3.1 · лучший генератор видео**\n\n"
        "✏️ Нейросеть создает качественные 8 секундные видео, может имитировать голоса, "
        "сопровождать видео звуковой дорожкой и учитывать ваши пожелания.\n\n"
        "📸 При желании можно прикрепить 1 фото с промптом и создать видео на его основе.\n\n"
        "📷 1️⃣:2️⃣ (начальный кадр / завершающий кадр). Прикрепите два фото в одном запросе "
        "и получите видео на их основе. При желании можете прикрепить описание.\n\n"
        "#️⃣ Изучите гайд для того, чтобы создавать качественные видео и получать предсказуемые результаты.\n\n"
        "⚙️ **Параметры**\n"
        "Модель: Veo 3.1 Fast\n"
        "Формат: 16:9\n"
        "Сид: 0\n\n"
        f"🔹 Баланса хватит на {videos_available} видео. 1 видео = {format_token_amount(veo_billing.tokens_per_generation)} токенов."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="veo", image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.sora")
async def start_sora(callback: CallbackQuery, state: FSMContext, user: User):
    from app.bot.keyboards.inline import sora_main_keyboard
    from app.bot.states.media import SoraSettings
    from app.core.billing_config import get_sora_tokens_cost

    # Get or create Sora settings from FSM
    data = await state.get_data()
    sora_settings = SoraSettings.from_dict(data)

    total_tokens = await get_available_tokens(user.id)
    tokens_per_video = get_sora_tokens_cost(sora_settings.quality, sora_settings.duration)
    videos_available = int(total_tokens / tokens_per_video) if total_tokens > 0 else 0

    text = (
        "☁️ **Sora 2 · вирусные ролики с озвучкой**\n\n"
        "✏️ Нейросеть создает видео длиной до 15 секунд, в котором может быть звук, "
        "возможна озвучка сцен и персонажей в кадре, смена локаций и т.д.\n\n"
        "📸 При желании можно прикрепить 1 фото с промптом и создать видео на его основе.\n\n"
        "⛔️ Sora не может озвучивать людей на фото и делать так, чтобы они учавствовали в кадре. "
        "Отправляйте фото без людей в кадре.\n\n"
        f"⚙️ **Параметры**\n"
        f"{sora_settings.get_display_settings()}\n\n"
        "💰 **Стоимость:** Sora 2 — 7 000т./1 сек., Sora 2 Pro (720P) — 20 000т./1 сек.\n\n"
        f"🔹 Баланса хватит на {videos_available} видео. "
        f"1 видео = {format_token_amount(tokens_per_video)} токенов"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    settings_dict = sora_settings.to_dict()
    await state.update_data(service="sora", image_path=None, photo_caption_prompt=None, **settings_dict)

    try:
        await callback.message.edit_text(text, reply_markup=sora_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=sora_main_keyboard())
    await callback.answer()


# Sora 2 settings handlers
@router.callback_query(F.data == "sora.settings")
async def sora_settings_menu(callback: CallbackQuery, state: FSMContext, user: User):
    from app.bot.keyboards.inline import sora_settings_keyboard
    text = "⚙️ **Настройки Sora 2**\n\nВыберите параметр для изменения:"
    try:
        await callback.message.edit_text(text, reply_markup=sora_settings_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=sora_settings_keyboard())
    await callback.answer()


@router.callback_query(F.data == "sora.settings.duration")
async def sora_duration_setting(callback: CallbackQuery, state: FSMContext, user: User):
    from app.bot.keyboards.inline import sora_duration_keyboard
    from app.bot.states.media import SoraSettings
    data = await state.get_data()
    sora_settings = SoraSettings.from_dict(data)
    text = "🕓 **Длительность видео**\n\nВыберите длительность:"
    try:
        await callback.message.edit_text(text, reply_markup=sora_duration_keyboard(sora_settings.duration))
    except Exception:
        await callback.message.answer(text, reply_markup=sora_duration_keyboard(sora_settings.duration))
    await callback.answer()


@router.callback_query(F.data.startswith("sora.set.duration:"))
async def sora_set_duration(callback: CallbackQuery, state: FSMContext, user: User):
    duration = int(callback.data.split(":")[1])
    await state.update_data(sora_duration=duration)
    await start_sora(callback, state, user)


@router.callback_query(F.data == "sora.settings.quality")
async def sora_quality_setting(callback: CallbackQuery, state: FSMContext, user: User):
    from app.bot.keyboards.inline import sora_quality_keyboard
    from app.bot.states.media import SoraSettings
    data = await state.get_data()
    sora_settings = SoraSettings.from_dict(data)
    text = "🎯 **Качество видео**\n\nВыберите качество:"
    try:
        await callback.message.edit_text(text, reply_markup=sora_quality_keyboard(sora_settings.quality))
    except Exception:
        await callback.message.answer(text, reply_markup=sora_quality_keyboard(sora_settings.quality))
    await callback.answer()


@router.callback_query(F.data.startswith("sora.set.quality:"))
async def sora_set_quality(callback: CallbackQuery, state: FSMContext, user: User):
    quality = callback.data.split(":")[1]
    await state.update_data(sora_quality=quality)
    await start_sora(callback, state, user)


@router.callback_query(F.data == "sora.settings.aspect_ratio")
async def sora_aspect_ratio_setting(callback: CallbackQuery, state: FSMContext, user: User):
    from app.bot.keyboards.inline import sora_aspect_ratio_keyboard
    from app.bot.states.media import SoraSettings
    data = await state.get_data()
    sora_settings = SoraSettings.from_dict(data)
    text = "📐 **Формат видео**\n\nВыберите формат:"
    try:
        await callback.message.edit_text(text, reply_markup=sora_aspect_ratio_keyboard(sora_settings.aspect_ratio))
    except Exception:
        await callback.message.answer(text, reply_markup=sora_aspect_ratio_keyboard(sora_settings.aspect_ratio))
    await callback.answer()


@router.callback_query(F.data.startswith("sora.set.aspect_ratio:"))
async def sora_set_aspect_ratio(callback: CallbackQuery, state: FSMContext, user: User):
    aspect_ratio = callback.data.split(":")[1]
    await state.update_data(sora_aspect_ratio=aspect_ratio)
    await start_sora(callback, state, user)


@router.callback_query(F.data == "bot.luma")
async def start_luma(callback: CallbackQuery, state: FSMContext, user: User):
    luma_billing = get_video_model_billing("luma")
    text = (
        "🌙 **Luma Dream Machine**\n\n"
        "Luma создаёт качественные видео по вашему описанию.\n\n"
        f"💰 **Стоимость:** Стоимость генерации видео: {format_token_amount(luma_billing.tokens_per_generation)} токенов\n\n"
        "🎨 **Режимы работы:**\n"
        "• **Text-to-Video:** Просто отправьте описание видео\n"
        "• **Image-to-Video:** Отправьте фото, затем описание\n\n"
        "✏️ **Отправьте описание видео ИЛИ фото**"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    # Clear old data when starting fresh session
    await state.update_data(service="luma", image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.hailuo")
async def start_hailuo(callback: CallbackQuery, state: FSMContext, user: User):
    total_tokens = await get_available_tokens(user.id)
    hailuo_billing = get_video_model_billing("hailuo")
    videos_available = int(total_tokens / hailuo_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "🎥 **Hailuo · создание видео**\n\n"
        "✏️ Отправьте мне описание того, что хотите видеть на вашем видео. "
        "Сформулируйте конкретный запрос, например:\n"
        "└ Она словно сошла с кисти Вермеера, ее жемчужная серьга поблескивает. "
        "Эти загадочные глаза выходят за пределы холста, губы изгибаются в тонкой, элегантной улыбке, обращенной ко мне..\n"
        "└ Синее плюшевое существо на экране помешивает суп в кастрюле, от которого идет пар, "
        "после чего тарелка супа превращается в лёд, а синее плюшевое существо  удивляется этому..\n\n"
        "⚙️ **Настройки:**\n"
        "Версия: t2v-01\n"
        "Автоперевод: включен\n\n"
        "📝 Выбранная модель принимает только текстовый запрос, вы можете изменить модель на понравившуюся "
        "или прикрепить фото с текстом и я автоматически изменю модель на t2v-01-director.\n\n"
        f"🔹 Токенов хватит на {videos_available} запросов. "
        f"1 запрос = {format_token_amount(hailuo_billing.tokens_per_generation)} токенов."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="hailuo", image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.kling_effects")
async def start_kling_effects(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Kling Effects main menu with instructions."""
    kling_effects_billing = get_video_model_billing("kling-effects")
    total_tokens = await get_available_tokens(user.id)
    videos_available = int(total_tokens / kling_effects_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "✨ **Kling Эффекты**\n\n"
        "Создавайте потрясающие видео с 199+ эффектами!\n\n"
        "**Как использовать:**\n"
        "1️⃣ Выберите эффект из категорий\n"
        "2️⃣ Загрузите фото (1 или 2 в зависимости от эффекта)\n"
        "3️⃣ Получите видео с эффектом!\n\n"
        "**Категории эффектов:**\n"
        "• ⭐ Популярные — лучшие эффекты\n"
        "• 💃 Танцы — танцевальные движения\n"
        "• 🐾 Питомцы — для ваших любимцев\n"
        "• 🦸 Трансформации — превращения\n"
        "• 🪽 Крылья и магия — фантастика\n"
        "• 🎬 Кино эффекты — bullet time и др.\n"
        "• 👫 Для двоих — эффекты для 2 фото\n"
        "• 🎨 Стили — аниме, комиксы, 3D\n"
        "• 😂 Забавные — весёлые эффекты\n"
        "• 🎉 Праздники — день рождения и др.\n"
        "• 🎄 Рождество — зимняя тематика\n"
        "• 🎬 Действия — спорт и движение\n\n"
        f"💰 Стоимость: {format_token_amount(kling_effects_billing.tokens_per_generation)} токенов\n"
        f"🔹 Доступно: {videos_available} видео"
    )

    await state.clear()
    await state.update_data(service="kling_effects")

    try:
        await callback.message.edit_text(text, reply_markup=kling_effects_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_effects_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "kling_effects.categories")
async def kling_effects_categories(callback: CallbackQuery, state: FSMContext, user: User):
    """Show effect categories."""
    text = (
        "📁 **Выберите категорию эффектов**\n\n"
        "Эффекты сгруппированы по темам для удобного поиска."
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_effects_categories_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_effects_categories_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("kling_effects.category:"))
async def kling_effects_show_category(callback: CallbackQuery, state: FSMContext, user: User):
    """Show effects in a category."""
    from app.services.video.kling_effects_service import EFFECT_CATEGORIES

    category = callback.data.split(":")[1]
    cat_data = EFFECT_CATEGORIES.get(category, {})
    cat_name = cat_data.get("name", category)

    text = f"🎭 **{cat_name}**\n\nВыберите эффект:"

    try:
        await callback.message.edit_text(text, reply_markup=kling_effects_list_keyboard(category, page=0))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_effects_list_keyboard(category, page=0))
    await callback.answer()


@router.callback_query(F.data.startswith("kling_effects.page:"))
async def kling_effects_page(callback: CallbackQuery, state: FSMContext, user: User):
    """Navigate effect pages."""
    from app.services.video.kling_effects_service import EFFECT_CATEGORIES

    parts = callback.data.split(":")
    category = parts[1]
    page = int(parts[2])

    cat_data = EFFECT_CATEGORIES.get(category, {})
    cat_name = cat_data.get("name", category)

    text = f"🎭 **{cat_name}**\n\nВыберите эффект:"

    try:
        await callback.message.edit_text(text, reply_markup=kling_effects_list_keyboard(category, page=page))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_effects_list_keyboard(category, page=page))
    await callback.answer()


@router.callback_query(F.data.startswith("kling_effects.select:"))
async def kling_effects_select(callback: CallbackQuery, state: FSMContext, user: User):
    """Select an effect and show instructions."""
    from app.services.video.kling_effects_service import (
        is_dual_image_effect,
        get_effect_display_name,
        DUAL_IMAGE_EFFECTS
    )

    effect_id = callback.data.split(":")[1]
    effect_name = get_effect_display_name(effect_id)
    is_dual = is_dual_image_effect(effect_id)

    kling_effects_billing = get_video_model_billing("kling-effects")

    if is_dual:
        text = (
            f"🎭 **Эффект: {effect_name}**\n\n"
            f"⚠️ Этот эффект требует **2 фотографии**!\n\n"
            f"После подтверждения отправьте 2 фото:\n"
            f"• Первое фото — левая сторона\n"
            f"• Второе фото — правая сторона\n\n"
            f"💰 Стоимость: {format_token_amount(kling_effects_billing.tokens_per_generation)} токенов"
        )
    else:
        text = (
            f"🎭 **Эффект: {effect_name}**\n\n"
            f"После подтверждения отправьте **1 фотографию**.\n\n"
            f"📋 Требования к фото:\n"
            f"• Формат: JPG, JPEG, PNG\n"
            f"• Размер: до 10 МБ\n"
            f"• Мин. размер: 300x300 px\n"
            f"• Соотношение сторон: от 1:2.5 до 2.5:1\n\n"
            f"💰 Стоимость: {format_token_amount(kling_effects_billing.tokens_per_generation)} токенов"
        )

    # Save selected effect to state
    await state.update_data(
        service="kling_effects",
        kling_effect_id=effect_id,
        kling_effect_name=effect_name,
        kling_effect_is_dual=is_dual,
        kling_effect_images=[]
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_effects_confirm_keyboard(effect_id))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_effects_confirm_keyboard(effect_id))
    await callback.answer()


@router.callback_query(F.data.startswith("kling_effects.confirm:"))
async def kling_effects_confirm(callback: CallbackQuery, state: FSMContext, user: User):
    """Confirm effect and wait for photo(s)."""
    from app.services.video.kling_effects_service import is_dual_image_effect, get_effect_display_name

    effect_id = callback.data.split(":")[1]
    effect_name = get_effect_display_name(effect_id)
    is_dual = is_dual_image_effect(effect_id)

    # Set state to wait for photos
    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(
        service="kling_effects",
        kling_effect_id=effect_id,
        kling_effect_name=effect_name,
        kling_effect_is_dual=is_dual,
        kling_effect_images=[]
    )

    if is_dual:
        text = (
            f"📸 **Отправьте 2 фотографии**\n\n"
            f"Эффект: {effect_name}\n\n"
            f"Отправьте фото по одному. Первое фото будет слева, второе — справа."
        )
    else:
        text = (
            f"📸 **Отправьте 1 фотографию**\n\n"
            f"Эффект: {effect_name}\n\n"
            f"После загрузки начнётся генерация видео."
        )

    try:
        await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# Handler for when user clicks "Kling" from main menu
@router.callback_query(F.data == "bot.kling_main")
async def start_kling_choice(callback: CallbackQuery, state: FSMContext, user: User):
    """Open Kling AI choice menu."""
    text = (
        "🎞 Kling AI\n\n"
        "Выберите, что хотите создать:\n\n"
        "🌄 Создать фото — генерация изображений\n"
        "🎬 Создать видео — генерация видео по тексту/фото\n"
        "🕺 Motion Control — перенос движений с видео на изображение"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_choice_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_choice_keyboard())
    await callback.answer()


# Handler for Kling Image generation
@router.callback_query(F.data == "bot.kling_image")
async def start_kling_image(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling image generation with settings display."""
    await callback.answer()

    # Get or create Kling Image settings from FSM
    data = await state.get_data()
    kling_image_settings = KlingImageSettings.from_dict(data)

    # Calculate available generations
    total_tokens = await get_available_tokens(user.id)
    kling_image_billing = get_image_model_billing("kling-image")
    tokens_per_request = kling_image_billing.tokens_per_generation
    images_available = int(total_tokens / tokens_per_request) if total_tokens > 0 else 0

    text = (
        "🎞 **Kling AI - Генерация изображений**\n\n"
        "Отправьте текстовый промпт для генерации изображения.\n\n"
        "📷 Вы также можете отправить фото с подписью для режима image-to-image.\n\n"
        "**Примеры:**\n"
        "• Закат над океаном в стиле аниме\n"
        "• Футуристический город с летающими машинами\n"
        "• Портрет кота в королевской одежде\n\n"
        f"⚙️ **Текущие настройки:**\n"
        f"{kling_image_settings.get_display_settings()}\n\n"
        f"🔹 Токенов хватит на {images_available} изображений.\n"
        f"1 изображение = {format_token_amount(tokens_per_request)} токенов."
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    # Save settings to state
    settings_dict = kling_image_settings.to_dict()
    await state.update_data(
        service="kling_image",
        reference_image_path=None,
        **settings_dict
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_image_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_image_main_keyboard())


# Handler for Kling Video generation (renamed from bot.kling)
@router.callback_query(F.data == "bot.kling_video")
async def start_kling_video(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling video generation with settings."""
    # Get or create Kling settings from FSM
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    total_tokens = await get_available_tokens(user.id)
    tokens_per_request = get_kling_tokens_cost(kling_settings.version, kling_settings.duration)
    videos_available = int(total_tokens / tokens_per_request) if total_tokens > 0 else 0

    # Build version info text
    if kling_settings.version == "2.5":
        version_info = (
            "📷 Вы выбрали версию 2.5 Turbo: эта версия может принять до двух фото "
            "с промптом в одном запросе. Можно использовать как начальный кадр / конечный кадр."
        )
    else:
        version_info = f"📷 Вы выбрали версию {kling_settings.version}."

    text = (
        "🎞 Kling · меняй реальность\n\n"
        "✏️ Отправьте мне описание того, что хотите видеть на вашем видео, например:\n"
        "└ Оживи моё фото и сделай так, чтобы я улыбался и махал рукой в камеру. (прикрепите своё фото или фото близкого).\n"
        "└ Неоновое иайдзюцу: киберпанк-самурай в действии. (прикрепите своё фото).\n\n"
        f"{version_info}\n\n"
        f"⚙️ Настройки (выбранные настройки):\n"
        f"{kling_settings.get_display_settings()}\n\n"
        f"🔹 Токенов хватит на {videos_available} запросов.\n"
        f"1 запрос = {format_token_amount(tokens_per_request)} токенов."
    )

    await state.set_state(MediaState.kling_waiting_for_prompt)
    # Save Kling settings and reset images
    settings_dict = kling_settings.to_dict()
    settings_dict["kling_images"] = []  # Reset collected images
    await state.update_data(
        service="kling",
        image_path=None,
        photo_caption_prompt=None,
        **settings_dict
    )

    # Try to edit message, fall back to answer if it fails (e.g., message is a photo)
    try:
        await callback.message.edit_text(text, reply_markup=kling_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_main_keyboard())
    await callback.answer()


# ======================
# KLING SETTINGS HANDLERS
# ======================

@router.callback_query(F.data == "kling.settings")
async def kling_settings_menu(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Kling settings menu."""
    text = (
        "⚙️ Настройки генерации видео Kling\n\n"
        "Выберите параметр для изменения:"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_settings_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_settings_keyboard())
    await callback.answer()


@router.callback_query(F.data == "kling.settings.aspect_ratio")
async def kling_settings_aspect_ratio(callback: CallbackQuery, state: FSMContext, user: User):
    """Show aspect ratio selection for Kling."""
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    text = (
        "📐 Выберите соотношение сторон у генерируемого видео в Kling.\n\n"
        "1:1 — квадратный формат видео, востребованный в социальных сетях, таких как VK, "
        "особенно для постов и рекламы. Этот формат обеспечивает равные размеры по ширине "
        "и высоте, что делает его удобным для мобильных устройств.\n\n"
        "16:9 — наиболее распространенное соотношение сторон, используемое для кино, "
        "YouTube и VK Video.\n\n"
        "9:16 — вертикальный формат, идеальный для Stories и мобильных платформ."
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_aspect_ratio_keyboard(kling_settings.aspect_ratio)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_aspect_ratio_keyboard(kling_settings.aspect_ratio)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling.set.aspect_ratio:"))
async def kling_set_aspect_ratio(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling aspect ratio."""
    aspect_ratio = callback.data.split(":")[1]

    await state.update_data(kling_aspect_ratio=aspect_ratio)

    await callback.answer(f"✅ Формат видео установлен: {aspect_ratio}")
    # Return to main Kling menu
    await start_kling_video(callback, state, user)


@router.callback_query(F.data == "kling.settings.duration")
async def kling_settings_duration(callback: CallbackQuery, state: FSMContext, user: User):
    """Show duration selection for Kling."""
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    text = "🕓 Выберите длительность видео в Kling."

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_duration_keyboard(kling_settings.duration)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_duration_keyboard(kling_settings.duration)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling.set.duration:"))
async def kling_set_duration(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling duration."""
    duration = int(callback.data.split(":")[1])

    await state.update_data(kling_duration=duration)

    await callback.answer(f"✅ Длительность установлена: {duration} секунд")
    # Return to main Kling menu
    await start_kling_video(callback, state, user)


@router.callback_query(F.data == "kling.settings.version")
async def kling_settings_version(callback: CallbackQuery, state: FSMContext, user: User):
    """Show version selection for Kling."""
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    text = "🔢 Выберите версию Kling."

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_version_keyboard(kling_settings.version)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_version_keyboard(kling_settings.version)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling.set.version:"))
async def kling_set_version(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling version."""
    version = callback.data.split(":")[1]

    await state.update_data(kling_version=version)

    await callback.answer(f"✅ Версия установлена: {version}")
    # Return to main Kling menu
    await start_kling_video(callback, state, user)


@router.callback_query(F.data == "kling.settings.auto_translate")
async def kling_settings_auto_translate(callback: CallbackQuery, state: FSMContext, user: User):
    """Show auto-translate selection for Kling."""
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    text = "🔤 Переводить ваш запрос на английский с любого языка?"

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_auto_translate_keyboard(kling_settings.auto_translate)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_auto_translate_keyboard(kling_settings.auto_translate)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling.set.auto_translate:"))
async def kling_set_auto_translate(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling auto-translate."""
    value = callback.data.split(":")[1] == "yes"

    await state.update_data(kling_auto_translate=value)

    status = "включен" if value else "выключен"
    await callback.answer(f"✅ Автоперевод {status}")
    # Return to main Kling menu
    await start_kling_video(callback, state, user)


# ======================
# KLING IMAGE SETTINGS HANDLERS
# ======================

@router.callback_query(F.data == "kling_image.settings")
async def kling_image_settings_menu(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Kling image settings menu."""
    text = (
        "⚙️ **Настройки генерации изображений Kling**\n\n"
        "Выберите параметр для изменения:"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_image_settings_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_image_settings_keyboard())
    await callback.answer()


@router.callback_query(F.data == "kling_image.settings.aspect_ratio")
async def kling_image_settings_aspect_ratio(callback: CallbackQuery, state: FSMContext, user: User):
    """Show aspect ratio selection for Kling image."""
    data = await state.get_data()
    kling_image_settings = KlingImageSettings.from_dict(data)

    text = (
        "📐 **Выберите формат изображения**\n\n"
        "• 1:1 — квадратный\n"
        "• 16:9 — широкоформатный\n"
        "• 9:16 — вертикальный\n"
        "• 4:3 — классический\n"
        "• 3:4 — портретный"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_image_aspect_ratio_keyboard(kling_image_settings.aspect_ratio)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_image_aspect_ratio_keyboard(kling_image_settings.aspect_ratio)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling_image.set.aspect_ratio:"))
async def kling_image_set_aspect_ratio(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling image aspect ratio."""
    ratio = callback.data.split(":")[1]

    await state.update_data(kling_image_aspect_ratio=ratio)

    await callback.answer(f"✅ Формат: {ratio}")
    # Return to main Kling image menu
    await start_kling_image(callback, state, user)


@router.callback_query(F.data == "kling_image.settings.model")
async def kling_image_settings_model(callback: CallbackQuery, state: FSMContext, user: User):
    """Show model selection for Kling image."""
    data = await state.get_data()
    kling_image_settings = KlingImageSettings.from_dict(data)

    text = (
        "🔢 **Выберите версию модели**\n\n"
        "• **Kling v1** — базовая версия\n"
        "• **Kling v1.5** — поддержка референсов (лицо/объект)\n"
        "• **Kling v2** — улучшенное качество"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_image_model_keyboard(kling_image_settings.model)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_image_model_keyboard(kling_image_settings.model)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling_image.set.model:"))
async def kling_image_set_model(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling image model."""
    model = callback.data.split(":")[1]

    await state.update_data(kling_image_model=model)

    model_names = {
        "kling-v1": "Kling v1",
        "kling-v1-5": "Kling v1.5",
        "kling-v2": "Kling v2",
    }
    await callback.answer(f"✅ Модель: {model_names.get(model, model)}")
    # Return to main Kling image menu
    await start_kling_image(callback, state, user)


@router.callback_query(F.data == "kling_image.settings.resolution")
async def kling_image_settings_resolution(callback: CallbackQuery, state: FSMContext, user: User):
    """Show resolution selection for Kling image."""
    data = await state.get_data()
    kling_image_settings = KlingImageSettings.from_dict(data)

    text = (
        "📏 **Выберите разрешение**\n\n"
        "• **1K** — стандартное разрешение (быстрее)\n"
        "• **2K** — высокое разрешение (больше деталей)"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_image_resolution_keyboard(kling_image_settings.resolution)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_image_resolution_keyboard(kling_image_settings.resolution)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling_image.set.resolution:"))
async def kling_image_set_resolution(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling image resolution."""
    resolution = callback.data.split(":")[1]

    await state.update_data(kling_image_resolution=resolution)

    res_names = {"1k": "1K", "2k": "2K"}
    await callback.answer(f"✅ Разрешение: {res_names.get(resolution, resolution)}")
    # Return to main Kling image menu
    await start_kling_image(callback, state, user)


@router.callback_query(F.data == "kling_image.settings.auto_translate")
async def kling_image_settings_auto_translate(callback: CallbackQuery, state: FSMContext, user: User):
    """Show auto-translate selection for Kling image."""
    data = await state.get_data()
    kling_image_settings = KlingImageSettings.from_dict(data)

    text = "🔤 **Автоперевод**\n\nПереводить ваш запрос на английский автоматически?"

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_image_auto_translate_keyboard(kling_image_settings.auto_translate)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_image_auto_translate_keyboard(kling_image_settings.auto_translate)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("kling_image.set.auto_translate:"))
async def kling_image_set_auto_translate(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Kling image auto-translate."""
    value = callback.data.split(":")[1] == "yes"

    await state.update_data(kling_image_auto_translate=value)

    status = "включен" if value else "выключен"
    await callback.answer(f"✅ Автоперевод {status}")
    # Return to main Kling image menu
    await start_kling_image(callback, state, user)


# ======================
# IMAGE GENERATION
# ======================

@router.callback_query(F.data == "bot.gpt_image")
async def start_gpt_image(callback: CallbackQuery, state: FSMContext, user: User):
    # Clean up any old images
    await cleanup_temp_images(state)
    dalle_billing = get_image_model_billing("dalle3")
    total_tokens = await get_available_tokens(user.id)
    requests_available = int(total_tokens / dalle_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "💥 **GPT Image 1.5 · лучший генератор изображений**\n\n"
        "📖 **Пишите запрос на любом языке:**\n"
        "– Эта модель понимает конкретно каждое ваше слово: на русском, на английском и любом языке;\n"
        "– Попросите её, например, создать постер с приглашением на мероприятие (укажите всю информацию о нём) или крутых котов в очках (как люди в черном).\n\n"
        "📷 **Можете прикрепить до 3 фото в одном сообщении c запросом:**\n"
        "– Прикрепите несколько фото с разными объектами и, например, попросите их соединить во что-то.\n\n"
        "💅 **Указывайте стиль генерации в запросе:**\n"
        "– Например: реалистичный стиль, стиль студии ghilbi (можете прикрепить свое фото) или любой другой;\n\n"
        "📐 **Формат фото:** 1:1\n\n"
        f"🔹 Токенов хватит на {requests_available} запросов. 1 фото = {format_token_amount(dalle_billing.tokens_per_generation)} токенов\n\n"
        "✏️ **Отправьте описание изображения ИЛИ фото**"
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="dalle", reference_image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "bot.nano")
async def start_nano(callback: CallbackQuery, state: FSMContext, user: User):
    # Clean up any old images
    await cleanup_temp_images(state)
    nano_billing = get_image_model_billing("nano-banana-image")

    text = (
        "🍌 **Nano Banana (Gemini 2.5 Flash Image)**\n\n"
        "Gemini 2.5 Flash Image создаёт изображения по текстовому описанию.\n\n"
        "📊 **Параметры:**\n"
        "• Форматы: 1:1, 16:9, 9:16, 3:4, 4:3\n"
        "• Высокое качество изображений\n\n"
        f"💰 **Стоимость генерации: {format_token_amount(nano_billing.tokens_per_generation)} токенов за изображение**\n\n"
        "🎨 **Режимы работы:**\n"
        "• **Text-to-Image:** Отправьте описание изображения\n"
        "• **Image-to-Image:** Отправьте **одно или несколько фото** + описание\n"
        "• **Множественная генерация:** Кнопка \"🎨 Создать несколько изображений\" (2-10 шт.)\n\n"
        "✏️ **Отправьте описание изображения ИЛИ фото (можно несколько)**\n\n"
        "**Примеры text-to-image:**\n"
        "• \"Кот в космосе среди звёзд\"\n"
        "• \"Закат на берегу океана с пальмами\"\n\n"
        "**Примеры image-to-image:**\n"
        "• Фото + \"Преобразуй в аниме стиль с яркими красками\"\n"
        "• Несколько фото + \"Сделай в стиле масляной живописи Ван Гога\"\n"
        "• Фото + \"Преобразуй в фэнтези иллюстрацию с магическими эффектами\""
    )

    await state.set_state(MediaState.waiting_for_image_prompt)

    # Get existing data or set defaults
    data = await state.get_data()
    current_ratio = data.get("nano_aspect_ratio", "auto")

    await state.update_data(
        service="nano_banana",
        nano_is_pro=False,
        reference_image_path=None,
        reference_image_paths=[],
        photo_caption_prompt=None,
        multi_images_count=0,
        nano_aspect_ratio=current_ratio  # Preserve existing format or set default
    )

    await callback.message.answer(text, reply_markup=nano_banana_keyboard(is_pro=False), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "bot.nano_pro")
async def start_nano_pro(callback: CallbackQuery, state: FSMContext, user: User):
    # Clean up any old images
    await cleanup_temp_images(state)
    banana_billing = get_image_model_billing("banana-pro")

    text = (
        "🍌✨ **Banana PRO (Gemini 3 Pro Image)**\n\n"
        "Gemini 3 Pro Image - это новейшая модель с улучшенными возможностями генерации.\n\n"
        "📊 **Параметры:**\n"
        "• Форматы: 1:1, 16:9, 9:16, 4:3, 3:4 и другие\n"
        "• Размеры: 2K, 4K\n"
        "• Высочайшее качество изображений\n"
        "• Улучшенная генерация текста на изображениях\n\n"
        f"💰 **Стоимость генерации: {format_token_amount(banana_billing.tokens_per_generation)} токенов за изображение**\n\n"
        "🎨 **Режимы работы:**\n"
        "• **Text-to-Image:** Отправьте описание изображения\n"
        "• **Image-to-Image:** Отправьте **одно или несколько фото** + описание\n"
        "• **Множественная генерация:** Кнопка \"🎨 Создать несколько изображений\" (2-10 шт.)\n"
        "• Поддержка Google Search для актуальной информации\n\n"
        "✏️ **Отправьте описание изображения ИЛИ фото (можно несколько)**\n\n"
        "**Примеры:**\n"
        "• \"Инфографика о текущей погоде в Токио\"\n"
        "• \"Фотореалистичный портрет кота в космосе в 4K\"\n"
        "• Несколько фото + \"Преобразуй в высококачественную иллюстрацию\""
    )

    await state.set_state(MediaState.waiting_for_image_prompt)

    # Get existing data or set defaults
    data = await state.get_data()
    current_ratio = data.get("nano_aspect_ratio", "auto")

    await state.update_data(
        service="nano_banana",
        nano_is_pro=True,
        reference_image_path=None,
        reference_image_paths=[],
        photo_caption_prompt=None,
        multi_images_count=0,
        nano_aspect_ratio=current_ratio  # Preserve existing format or set default
    )

    await callback.message.answer(text, reply_markup=nano_banana_keyboard(is_pro=True), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "bot.midjourney")
async def start_midjourney(callback: CallbackQuery, state: FSMContext, user: User):
    """Midjourney image generation."""
    from app.bot.keyboards.inline import midjourney_main_keyboard

    await cleanup_temp_images(state)

    mj_billing = get_image_model_billing("midjourney")
    total_tokens = await get_available_tokens(user.id)
    images_available = int(total_tokens / mj_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "🌆 **Midjourney · генерация изображений**\n\n"
        "✏️ Отправьте текстовое описание изображения, которое хотите создать.\n\n"
        "**Примеры:**\n"
        "• Futuristic cityscape at sunset, cinematic lighting, 8k\n"
        "• A cute cat wearing a space helmet, floating in galaxy\n"
        "• Portrait of a samurai in neon rain, cyberpunk style\n\n"
        "⚙️ **Параметры:**\n"
        "Версия: 7\n"
        "Скорость: fast\n"
        "Формат: 16:9\n\n"
        f"🔹 Баланса хватит на {images_available} изображений. "
        f"1 изображение = {format_token_amount(mj_billing.tokens_per_generation)} токенов"
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="midjourney", reference_image_path=None, photo_caption_prompt=None)

    try:
        await callback.message.edit_text(text, reply_markup=midjourney_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=midjourney_main_keyboard())
    await callback.answer()


async def start_midjourney_video(callback: CallbackQuery, state: FSMContext, user: User):
    """Midjourney Video (image-to-video) generation."""
    from app.bot.keyboards.inline import midjourney_video_main_keyboard

    mj_billing = get_image_model_billing("midjourney")
    total_tokens = await get_available_tokens(user.id)
    images_available = int(total_tokens / mj_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "🌆 **Midjourney Video · Image-to-Video**\n\n"
        "✏️ Отправьте фото с описанием, чтобы создать видео на его основе.\n\n"
        "**Как использовать:**\n"
        "1. Прикрепите фото\n"
        "2. Добавьте описание движения/действия в подписи\n\n"
        "**Примеры промптов:**\n"
        "• Camera slowly zooms in, wind blows through hair\n"
        "• The character turns and smiles at the camera\n\n"
        f"🔹 Баланса хватит на {images_available} запросов. "
        f"1 запрос = {format_token_amount(mj_billing.tokens_per_generation)} токенов"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="midjourney_video", image_path=None, photo_caption_prompt=None)

    try:
        await callback.message.edit_text(text, reply_markup=midjourney_video_main_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=midjourney_video_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.recraft")
async def start_recraft(callback: CallbackQuery, state: FSMContext, user: User):
    """Recraft AI image generation."""
    # Clean up any old images
    await cleanup_temp_images(state)
    recraft_billing = get_image_model_billing("recraft")
    total_tokens = await get_available_tokens(user.id)
    requests_available = int(total_tokens / recraft_billing.tokens_per_generation) if total_tokens > 0 else 0

    text = (
        "🎨 **Recraft · нарисуем что-нибудь?**\n\n"
        "Напишите мне, что хотите видеть на вашем фото. Эта нейросеть хорошо понимает русский язык, но если вам так не кажется — включите автоперевод.\n"
        "Вы можете прикрепить фото к запросу и я постараюсь его изменить согласно вашему промпту.\n\n"
        "⚙️ **Настройки**\n"
        "Стиль: Реалистичное изображение\n"
        "Размер: 1024x1024\n"
        "Автоперевод: отключен\n\n"
        "📸 Вы выбрали реалистичный стиль, генерации будут получатся более приближенными к реальным фотографиям.\n\n"
        f"🔹 Токенов хватит на {requests_available} запросов. 1 фото = {format_token_amount(recraft_billing.tokens_per_generation)} токенов.\n\n"
        "✏️ **Отправьте описание изображения**"
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="recraft", reference_image_path=None, photo_caption_prompt=None)

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


# ======================
# AUDIO SERVICES
# ======================

# Note: Suno handler moved to suno_handler.py for better organization and step-by-step creation


@router.callback_query(F.data == "bot.whisper")
async def start_whisper(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "🎙 **Whisper - Расшифровка голоса**\n\n"
        "OpenAI Whisper распознает речь и превращает её в текст.\n\n"
        "📊 **Возможности:**\n"
        "• Точная расшифровка на русском и других языках\n"
        "• Поддержка различных аудио форматов\n"
        "• Высокая точность распознавания\n\n"
        "💰 **Стоимость:** ~1,000 токенов за минуту аудио\n\n"
        "🎵 **Отправьте аудио или голосовое сообщение**"
    )

    await state.set_state(MediaState.waiting_for_whisper_audio)

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.whisper_tts")
async def start_tts(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "🗣 **OpenAI TTS – Text to Speech**\n\n"
        "Превратите текст в естественную речь.\n\n"
        "💰 **Стоимость:** ~200 токенов за запрос\n\n"
        "🎤 **Доступные голоса:**\n"
        "• alloy - Нейтральный голос\n"
        "• echo - Мужской голос\n"
        "• fable - Британский акцент\n"
        "• onyx - Глубокий мужской\n"
        "• nova - Женский голос\n"
        "• shimmer - Мягкий женский\n\n"
        "✏️ **Отправьте текст для озвучки**"
    )

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="tts")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.gpt_vision")
async def start_gpt_vision(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "👁 **GPT Image 1 - Анализ изображений**\n\n"
        "GPT-4 Vision может анализировать изображения и отвечать на вопросы о них.\n\n"
        "📊 **Возможности:**\n"
        "• Детальное описание содержимого\n"
        "• Распознавание объектов и текста\n"
        "• Анализ данных из графиков\n"
        "• Ответы на вопросы об изображении\n\n"
        "💰 **Стоимость:** ~1,000 токенов за запрос\n\n"
        "📸 **Отправьте изображение для анализа**"
    )

    await state.set_state(MediaState.waiting_for_vision_image)

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# IMAGE PROCESSING
# ======================

@router.callback_query(F.data == "bot.pi_upscale")
async def start_upscale(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Улучшение качества фото\n\n"
        "Увеличьте разрешение и улучшите качество изображения.\n\n"
        "Стоимость: ~2,000 токенов\n\n"
        "Отправьте изображение."
    )

    await state.set_state(MediaState.waiting_for_upscale_image)
    await state.update_data(service="upscale")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.pi_remb")
async def start_remove_bg(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Удаление фона\n\n"
        "Стоимость: ~500 токенов\n\n"
        "Отправьте изображение для удаления фона."
    )

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="remove_bg")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.pi_repb")
async def start_replace_bg(callback: CallbackQuery, state: FSMContext, user: User):
    # Clean up any old images
    await cleanup_temp_images(state)

    text = (
        "🖼 **Замена фона (Gemini 2.5 Flash Image)**\n\n"
        "Умная замена фона с помощью ИИ Gemini.\n\n"
        "💰 **Стоимость:** ~2,000 токенов\n\n"
        "📝 **Как использовать:**\n"
        "1. Отправьте фото\n"
        "2. Отправьте описание нового фона\n\n"
        "**Примеры:**\n"
        "• \"Белый фон\"\n"
        "• \"Пляж с пальмами на закате\"\n"
        "• \"Городская улица ночью\"\n"
        "• \"Абстрактный градиент от синего к фиолетовому\"\n\n"
        "📸 **Отправьте изображение для замены фона**"
    )

    await state.set_state(MediaState.waiting_for_replace_bg_image)
    await state.update_data(service="replace_bg")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode="Markdown")
    await callback.answer()


# ======================
# FSM HANDLERS - VIDEO
# ======================

@router.message(MediaState.waiting_for_video_prompt, F.photo)
async def process_video_photo(message: Message, state: FSMContext, user: User):
    """Handle photo for image-to-video generation."""
    data = await state.get_data()
    service_name = data.get("service", "veo")

    # Download the photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    # ИСПРАВЛЕНО: используем TempFileManager для генерации уникального пути
    # вместо file_id который может конфликтовать при повторной загрузке
    temp_path = get_temp_file_path(prefix="video_input", suffix=".jpg", user_id=user.id)

    await message.bot.download_file(file.file_path, temp_path)

    # Save absolute image path to state
    await state.update_data(image_path=str(temp_path))

    # Check if photo has caption (description)
    if message.caption and message.caption.strip():
        # User sent photo with description - process immediately
        # Save caption as prompt in state
        await state.update_data(photo_caption_prompt=message.caption.strip())

        # Route to appropriate video service
        if service_name == "veo":
            await process_veo_video(message, user, state)
        elif service_name == "sora":
            await process_sora_video(message, user, state)
        elif service_name == "luma":
            await process_luma_video(message, user, state)
        elif service_name == "hailuo":
            await process_hailuo_video(message, user, state)
        elif service_name == "kling":
            await process_kling_video(message, user, state)
        elif service_name == "kling_effects":
            await process_kling_effects(message, user, state)
        elif service_name == "midjourney_video":
            await process_midjourney_video(message, user, state)
    else:
        # No caption
        # For kling_effects, we don't need a caption - the effect ID is the action
        if service_name == "kling_effects":
            await process_kling_effects(message, user, state)
        else:
            # Ask for description for other services
            await message.answer(
                "✅ Фото получено!\n\n"
                "📝 Теперь отправьте описание видео, которое вы хотите создать на основе этого фото.\n\n"
                "**Примеры:**\n"
                "• \"Оживи это фото, добавь плавное движение\"\n"
                "• \"Сделай так, чтобы волосы развевались на ветру\"\n"
                "• \"Добавь падающие снежинки и плавное движение камеры\""
            )


@router.message(MediaState.waiting_for_video_prompt, F.text)
async def process_video_prompt(message: Message, state: FSMContext, user: User):
    # CRITICAL FIX: Ignore commands (text starting with /)
    # Commands should NOT be processed as prompts
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    # Check message length (max 2000 characters)
    if message.text and len(message.text) > 2000:
        await message.answer(
            "⚠️ Описание слишком длинное!\n\n"
            f"Максимальная длина: 2000 символов\n"
            f"Ваше описание: {len(message.text)} символов\n\n"
            "Пожалуйста, сократите описание и попробуйте снова."
        )
        return

    data = await state.get_data()
    service_name = data.get("service", "sora")

    display_names = {
        "veo": "Veo 3.1",
        "sora": "Sora 2",
        "luma": "Luma Dream Machine",
        "hailuo": "Hailuo",
        "kling": "Kling AI",
        "kling_effects": "Kling Effects",
        "midjourney_video": "Midjourney Video",
    }
    display = display_names.get(service_name, service_name)

    # Route to appropriate video service
    if service_name == "veo":
        await process_veo_video(message, user, state)
    elif service_name == "sora":
        await process_sora_video(message, user, state)
    elif service_name == "luma":
        await process_luma_video(message, user, state)
    elif service_name == "hailuo":
        await process_hailuo_video(message, user, state)
    elif service_name == "kling" or service_name == "kling_effects":
        await process_kling_video(message, user, state, is_effects=(service_name == "kling_effects"))
    elif service_name == "midjourney_video":
        await process_midjourney_video(message, user, state)
    else:
        await message.answer(
            f"Функция генерации видео ({display}) находится в разработке.\n"
            f"Ваш запрос получен: {message.text[:100]}..."
        )
        await state.clear()


# ======================
# FSM HANDLERS - KLING VIDEO GENERATION
# ======================

@router.message(MediaState.kling_waiting_for_prompt, F.photo)
async def process_kling_photo(message: Message, state: FSMContext, user: User):
    """Handle photo for Kling video generation (supports up to 2 photos for v2.5)."""
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    # Get current images list
    kling_images = data.get("kling_images", [])

    # Download the photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    temp_path = get_temp_file_path(prefix="kling_input", suffix=".jpg", user_id=user.id)
    await message.bot.download_file(file.file_path, temp_path)

    # Resize image if needed
    resize_image_if_needed(str(temp_path), max_size_mb=10.0, max_dimension=2048)

    # Add image to list
    kling_images.append(str(temp_path))
    await state.update_data(kling_images=kling_images)

    # Check max images based on version
    max_images = 2 if kling_settings.version == "2.5" else 1

    if len(kling_images) > max_images:
        # Too many images - remove the last one and warn
        cleanup_temp_file(str(temp_path))
        kling_images.pop()
        await state.update_data(kling_images=kling_images)

        if max_images == 1:
            await message.answer(
                f"⚠️ Версия {kling_settings.version} поддерживает только 1 изображение.\n"
                "Переключитесь на версию 2.5 для использования двух изображений."
            )
        else:
            await message.answer("⚠️ Максимум 2 изображения для версии 2.5.")
        return

    # Check if photo has caption (description) - process immediately
    if message.caption and message.caption.strip():
        await state.update_data(photo_caption_prompt=message.caption.strip())
        await process_kling_video(message, user, state)
    else:
        # No caption - show status
        photos_count = len(kling_images)

        if kling_settings.version == "2.5":
            if photos_count == 1:
                await message.answer(
                    f"✅ Фото {photos_count} сохранено! (начальный кадр)\n\n"
                    "📸 Вы можете:\n"
                    "• Загрузить второе фото (конечный кадр)\n"
                    "• Отправить текстовый промпт для начала генерации\n\n"
                    "💡 В версии 2.5 можно использовать 2 фото как начальный и конечный кадры."
                )
            else:
                await message.answer(
                    f"✅ Фото {photos_count} сохранено! (конечный кадр)\n\n"
                    "📝 Теперь отправьте текстовое описание видео."
                )
        else:
            await message.answer(
                "✅ Фото получено!\n\n"
                "📝 Теперь отправьте описание видео, которое хотите создать."
            )


@router.message(MediaState.kling_waiting_for_prompt, F.text)
async def process_kling_prompt(message: Message, state: FSMContext, user: User):
    """Process Kling video generation prompt."""
    # Ignore commands
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    # Check message length (max 2500 characters for Kling)
    if message.text and len(message.text) > 2500:
        await message.answer(
            "⚠️ Описание слишком длинное!\n\n"
            f"Максимальная длина: 2500 символов\n"
            f"Ваше описание: {len(message.text)} символов\n\n"
            "Пожалуйста, сократите описание и попробуйте снова."
        )
        return

    # Process Kling video generation
    await process_kling_video(message, user, state)


async def process_veo_video(message: Message, user: User, state: FSMContext):
    """Process Veo video generation with cost-guard protection."""
    # Get state data (check if image was provided)
    data = await state.get_data()

    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    image_path = data.get("image_path", None)

    # COST-GUARD: оценить стоимость с эконом-режимом (4 сек по умолчанию)
    # Пользователь может явно указать duration, иначе используется безопасный минимум
    duration = data.get("duration", None)  # None = будет использован default из cost_guard
    cost_estimate = cost_guard.estimate_cost("veo-3.1", duration=duration)

    # COST-GUARD: проверить rate limit
    allowed, rate_error = await cost_guard.check_rate_limit(user.id, "veo-3.1")
    if not allowed:
        # Clean up image if exists
        cleanup_temp_file(image_path)
        await message.answer(rate_error)
        await state.clear()
        return

    estimated_tokens = cost_estimate.estimated_tokens
    actual_duration = cost_estimate.duration_seconds

    # Показать предупреждение о стоимости
    cost_warning = (
        f"💰 **Стоимость генерации Veo 3.1:**\n\n"
        f"Длительность: {actual_duration} сек\n"
        f"Стоимость: {format_token_amount(estimated_tokens)} токенов (≈${cost_estimate.estimated_cost_usd:.2f})\n\n"
    )

    if cost_estimate.warning_message:
        cost_warning += f"{cost_estimate.warning_message}\n\n"

    # COST-GUARD: требовать подтверждение для дорогих запросов
    if cost_estimate.requires_confirmation:
        # TODO: В будущем добавить inline кнопки подтверждения
        # Пока просто информируем пользователя
        cost_warning += "⚠️ Это дорогая операция! Убедитесь что промпт правильный.\n\n"

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Clean up image if exists
            cleanup_temp_file(image_path)

            await message.answer(
                f"❌ Недостаточно токенов для генерации видео!\n\n"
                f"{cost_warning}"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send improved progress message with cost info
    mode_text = "image-to-video" if image_path else "text-to-video"
    progress_msg = await message.answer(
        f"🎬 Создаю видео в Veo 3.1 ({mode_text})...\n\n"
        f"⏱ Длительность: {actual_duration} сек\n"
        f"💰 Стоимость: {format_token_amount(estimated_tokens)} токенов\n\n"
        f"⏱ Создание может занять ~2-10 минут.\n"
        f"⚡️ Очень сильная нагрузка на сервис, но результат может появиться намного быстрее."
    )

    # Create service
    veo_service = VeoService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # ИСПРАВЛЕНО: используем actual_duration из cost_estimate (эконом-режим)
    # Generate video
    result = await veo_service.generate_video(
        prompt=prompt,
        progress_callback=update_progress,
        duration=actual_duration,  # Используем duration из cost_guard
        aspect_ratio="16:9",
        resolution="720p",
        image_path=image_path
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        mode_info = "image-to-video" if image_path else "text-to-video"
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name="Veo 3.1",
            tokens_used=result.tokens_used,
            user_tokens=user_tokens,
            prompt=prompt,
            mode=mode_info
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["veo"]["text"],
            action_callback=MODEL_ACTIONS["veo"]["callback"],
            file_path=result.video_path,
            file_type="video"
        )

        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=caption,
            reply_markup=builder.as_markup()
        )

        # Clean up
        try:
            pass  # os.remove(result.video_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("video_cleanup_failed", error=str(e))

        # Clean up input image if exists
        cleanup_temp_file(image_path)

        # COST-GUARD: логировать успешную генерацию
        await cost_guard.log_generation(
            user_id=user.id,
            model="veo-3.1",
            prompt=prompt,
            estimated_tokens=estimated_tokens,
            actual_tokens=result.tokens_used,
            estimated_cost_usd=cost_estimate.estimated_cost_usd,
            actual_cost_usd=(result.tokens_used / 1000) * 0.01,
            duration_seconds=actual_duration,
            status="success",
            mode=mode_info
        )

        await progress_msg.delete()

        # Clear image_path from state but keep service to allow new generation
        await state.update_data(image_path=None, photo_caption_prompt=None)
    else:
        # Clean up input image if exists
        cleanup_temp_file(image_path)

        # COST-GUARD: логировать ошибку
        await cost_guard.log_generation(
            user_id=user.id,
            model="veo-3.1",
            prompt=prompt,
            estimated_tokens=estimated_tokens,
            actual_tokens=0,
            estimated_cost_usd=cost_estimate.estimated_cost_usd,
            actual_cost_usd=0.0,
            duration_seconds=actual_duration,
            status="error",
            error=result.error
        )

        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации видео:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

        # Clear image_path from state but keep service to allow retry
        await state.update_data(image_path=None, photo_caption_prompt=None)


async def process_sora_video(message: Message, user: User, state: FSMContext):
    """Process Sora 2 video generation using callback-based flow.

    1. Reserve tokens
    2. Send createTask to Kie.ai with callBackUrl
    3. Save job to DB
    4. Return immediately — callback handler delivers the result
    """
    from app.bot.states.media import SoraSettings
    from app.core.billing_config import get_sora_tokens_cost
    from app.services.video_job_service import VideoJobService

    # Get state data
    data = await state.get_data()
    sora_settings = SoraSettings.from_dict(data)

    prompt = data.get("photo_caption_prompt") or message.text
    image_path = data.get("image_path", None)

    api_model = sora_settings.get_api_model(has_image=bool(image_path))
    estimated_tokens = get_sora_tokens_cost(sora_settings.quality, sora_settings.duration)

    # Step 1: Reserve tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.reserve_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            if image_path:
                cleanup_temp_file(image_path)
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    quality_text = "Pro" if sora_settings.quality == "pro" else "Stable"

    # Image-to-video not supported yet (needs CDN upload)
    if image_path:
        cleanup_temp_file(image_path)
        await message.answer(
            "⚠️ **Image-to-Video для Sora 2 временно недоступен**\n\n"
            "Sora 2 API требует загрузки изображения на CDN сервер.\n\n"
            "Используйте text-to-video режим или альтернативные сервисы:\n"
            "• 🌊 Veo 3.1 (поддерживает image-to-video)\n"
            "• 🎥 Hailuo (поддерживает image-to-video)",
            parse_mode="Markdown"
        )
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.rollback_tokens(user.id, estimated_tokens)
        await state.update_data(image_path=None, photo_caption_prompt=None)
        return

    # Step 2: Send progress message
    mode_text = "text-to-video"
    progress_msg = await message.answer(
        f"⏳ Ваше видео Sora 2 {quality_text} ({mode_text}, {sora_settings.duration}с) "
        f"добавлено в очередь на генерацию!\n\n"
        f"Мы отправим вам результат, как только он будет готов. "
        f"Это может занять несколько минут.\n\n"
        f"Вы можете продолжать пользоваться ботом."
    )

    # Step 3: Create task via Kie.ai API with callback
    sora_service = SoraService()
    try:
        task_id = await sora_service.create_task(
            prompt=prompt,
            model=api_model,
            aspect_ratio=sora_settings.aspect_ratio,
            n_frames=str(sora_settings.duration),
        )
    except Exception as e:
        logger.error("sora_create_task_failed", error=str(e), user_id=user.id)
        # Rollback tokens on API failure
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.rollback_tokens(user.id, estimated_tokens)
        await progress_msg.edit_text(
            f"❌ Ошибка создания задачи Sora 2:\n{str(e)[:200]}\n\n"
            f"💰 Токены возвращены на баланс.",
            parse_mode=None,
        )
        await state.update_data(image_path=None, photo_caption_prompt=None)
        return

    # Step 4: Save job to database
    try:
        async with async_session_maker() as session:
            job_service = VideoJobService(session)
            job = await job_service.create_job(
                user_id=user.id,
                provider="sora",
                model_id=api_model,
                prompt=prompt,
                input_data={
                    "aspect_ratio": sora_settings.aspect_ratio,
                    "n_frames": str(sora_settings.duration),
                    "quality": sora_settings.quality,
                    "quality_text": quality_text,
                },
                chat_id=message.chat.id,
                tokens_cost=estimated_tokens,
                progress_message_id=progress_msg.message_id,
            )
            # Store task_id from Kie.ai
            await job_service.update_job_status(
                job.id,
                "processing",
                task_id=task_id,
            )
            logger.info(
                "sora_job_created",
                job_id=job.id,
                task_id=task_id,
                user_id=user.id,
                model=api_model,
                tokens=estimated_tokens,
            )
    except Exception as e:
        logger.error("sora_job_save_failed", error=str(e), user_id=user.id)
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.rollback_tokens(user.id, estimated_tokens)
        await progress_msg.edit_text(
            f"❌ Ошибка сохранения задачи:\n{str(e)[:200]}\n\n"
            f"💰 Токены возвращены на баланс.",
            parse_mode=None,
        )
        await state.update_data(image_path=None, photo_caption_prompt=None)
        return

    # Done — handler returns, callback will deliver the result
    await state.update_data(image_path=None, photo_caption_prompt=None)


async def process_luma_video(message: Message, user: User, state: FSMContext):
    """Process Luma Dream Machine video generation."""
    # Get state data (check if image was provided)
    data = await state.get_data()

    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    image_path = data.get("image_path", None)

    luma_billing = get_video_model_billing("luma")
    estimated_tokens = luma_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Clean up image if exists
            if image_path:
                cleanup_temp_file(image_path)

            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    mode_text = "image-to-video" if image_path else "text-to-video"
    progress_msg = await message.answer(f"🎬 Инициализация Luma Dream Machine ({mode_text})...")
    luma_service = LumaService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Prepare keyframes if image provided
    # NOTE: Luma API требует URL изображения, а не локальный файл
    # "You should upload and use your own cdn image urls, currently this is the only way to pass an image"
    # Для текущей реализации мы отключаем image-to-video для Luma
    if image_path:
        # Clean up
        cleanup_temp_file(image_path)
        await progress_msg.edit_text(
            "⚠️ **Image-to-Video для Luma временно недоступен**\n\n"
            "Luma API требует загрузки изображения на CDN сервер, что находится в разработке.\n\n"
            "Используйте text-to-video режим или альтернативные сервисы:\n"
            "• 🌊 Veo 3.1 (поддерживает image-to-video)\n"
            "• 🎥 Hailuo (поддерживает image-to-video)",
            parse_mode="Markdown"
        )
        await state.clear()
        return

    # Text-to-video mode (no keyframes needed)
    result = await luma_service.generate_video(
        prompt=prompt,
        progress_callback=update_progress
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        mode_info = "image-to-video" if image_path else "text-to-video"
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name="Luma Dream Machine",
            tokens_used=result.tokens_used,
            user_tokens=user_tokens,
            prompt=prompt,
            mode=mode_info
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["luma"]["text"],
            action_callback=MODEL_ACTIONS["luma"]["callback"],
            file_path=result.video_path,
            file_type="video"
        )

        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=caption,
            reply_markup=builder.as_markup()
        )
        try:
            pass  # os.remove(result.video_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("video_cleanup_failed", error=str(e))

        # Clean up input image if exists
        if image_path:
            cleanup_temp_file(image_path)

        await progress_msg.delete()
    else:
        # Clean up input image if exists
        if image_path:
            cleanup_temp_file(image_path)

        try:
            await progress_msg.edit_text(f"❌ Ошибка: {result.error}", parse_mode=None)
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


async def process_hailuo_video(message: Message, user: User, state: FSMContext):
    """Process Hailuo (MiniMax) video generation."""
    # Get state data
    data = await state.get_data()
    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    hailuo_billing = get_video_model_billing("hailuo")
    estimated_tokens = hailuo_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    progress_msg = await message.answer("🎬 Инициализация Hailuo AI...")
    hailuo_service = HailuoService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    result = await hailuo_service.generate_video(
        prompt=prompt,
        progress_callback=update_progress
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name="Hailuo AI",
            tokens_used=result.tokens_used,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["hailuo"]["text"],
            action_callback=MODEL_ACTIONS["hailuo"]["callback"],
            file_path=result.video_path,
            file_type="video"
        )

        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=caption,
            reply_markup=builder.as_markup()
        )
        try:
            pass  # os.remove(result.video_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("video_cleanup_failed", error=str(e))
        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(f"❌ Ошибка: {result.error}", parse_mode=None)
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


async def process_kling_video(message: Message, user: User, state: FSMContext, is_effects: bool = False):
    """Process Kling AI video generation with configurable settings."""
    # Get state data (check if image was provided)
    data = await state.get_data()

    # Get Kling settings from FSM
    kling_settings = KlingSettings.from_dict(data)

    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text

    # Get images (single image or list of images for multi-image mode)
    images = data.get("kling_images", [])
    single_image = data.get("image_path", None)
    if single_image and single_image not in images:
        images = [single_image]

    # Calculate tokens based on version and duration
    if is_effects:
        kling_billing = get_video_model_billing("kling-effects")
        estimated_tokens = kling_billing.tokens_per_generation
    else:
        estimated_tokens = get_kling_tokens_cost(kling_settings.version, kling_settings.duration)

    # Check if user has enough tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Clean up images if exist
            for img_path in images:
                cleanup_temp_file(img_path)

            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {format_token_amount(estimated_tokens)} токенов\n"
                f"Доступно: {format_token_amount(e.details['available'])} токенов"
            )
            await state.clear()
            return

    # Validate image count based on version
    if len(images) > 2:
        for img_path in images:
            cleanup_temp_file(img_path)
        await message.answer("❌ Максимум 2 изображения поддерживаются.")
        await state.clear()
        return

    if len(images) == 2 and kling_settings.version != "2.5":
        for img_path in images:
            cleanup_temp_file(img_path)
        await message.answer("❌ Два изображения поддерживаются только в версии 2.5.")
        await state.clear()
        return

    # Determine mode
    if is_effects:
        service_name = "Kling Effects"
    else:
        service_name = f"Kling {kling_settings.version}"

    if len(images) == 0:
        mode_text = "text-to-video"
    elif len(images) == 1:
        mode_text = "image-to-video"
    else:
        mode_text = "multi-image-to-video"

    progress_msg = await message.answer(f"🎬 Инициализация {service_name} ({mode_text})...")
    kling_service = KlingService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Prepare kwargs for video generation
    api_model = get_kling_api_model(kling_settings.version) if not is_effects else "kling-v1.6-pro"

    result = await kling_service.generate_video(
        prompt=prompt,
        model=api_model,
        progress_callback=update_progress,
        images=images,
        duration=kling_settings.duration,
        aspect_ratio=kling_settings.aspect_ratio,
        version=kling_settings.version
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        tokens_used = estimated_tokens

        # Generate unified notification message
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name=service_name,
            tokens_used=tokens_used,
            user_tokens=user_tokens,
            prompt=prompt,
            mode=mode_text
        )

        # Create action keyboard
        callback_key = "kling_effects" if is_effects else "kling"
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS[callback_key]["text"],
            action_callback=MODEL_ACTIONS[callback_key]["callback"],
            file_path=result.video_path,
            file_type="video"
        )

        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=caption,
            reply_markup=builder.as_markup()
        )

        # Clean up input images
        for img_path in images:
            cleanup_temp_file(img_path)

        await progress_msg.delete()
    else:
        # Clean up input images
        for img_path in images:
            cleanup_temp_file(img_path)

        try:
            await progress_msg.edit_text(f"❌ Ошибка: {result.error}", parse_mode=None)
        except Exception:
            pass

    await state.clear()


async def process_kling_effects(message: Message, user: User, state: FSMContext):
    """Process Kling Effects video generation from photo(s)."""
    data = await state.get_data()

    # Get effect settings from state
    effect_id = data.get("kling_effect_id")
    effect_name = data.get("kling_effect_name", effect_id)
    is_dual = data.get("kling_effect_is_dual", False)
    kling_effect_images = data.get("kling_effect_images", [])

    if not effect_id:
        await message.answer("❌ Эффект не выбран. Пожалуйста, выберите эффект заново.")
        await state.clear()
        return

    # Get the image path from state (saved by process_video_photo)
    image_path = data.get("image_path")
    if not image_path:
        await message.answer("❌ Фото не найдено. Попробуйте отправить снова.")
        return

    # Add new image to the list
    kling_effect_images.append(image_path)
    await state.update_data(kling_effect_images=kling_effect_images)

    # Check if we have enough images
    required_images = 2 if is_dual else 1
    if len(kling_effect_images) < required_images:
        # Need more images
        await message.answer(
            f"✅ Получено {len(kling_effect_images)}/{required_images} фото\n\n"
            f"📸 Отправьте ещё {required_images - len(kling_effect_images)} фото"
        )
        return

    # We have all required images - proceed with generation
    kling_effects_billing = get_video_model_billing("kling-effects")
    estimated_tokens = kling_effects_billing.tokens_per_generation

    # Check if user has enough tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Clean up images
            for img_path in kling_effect_images:
                cleanup_temp_file(img_path)

            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {format_token_amount(estimated_tokens)} токенов\n"
                f"Доступно: {format_token_amount(e.details['available'])} токенов"
            )
            await state.clear()
            return

    progress_msg = await message.answer(f"🎬 Начинаю создание видео с эффектом «{effect_name}»...")

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate video with Kling Effects
    effects_service = KlingEffectsService()
    result = await effects_service.generate_effect_video(
        effect_scene=effect_id,
        image_paths=kling_effect_images,
        progress_callback=update_progress
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        tokens_used = estimated_tokens

        # Generate unified notification message
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name=f"Kling Effects ({effect_name})",
            tokens_used=tokens_used,
            user_tokens=user_tokens,
            prompt=f"Эффект: {effect_name}",
            mode="effect-video"
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["kling_effects"]["text"],
            action_callback=MODEL_ACTIONS["kling_effects"]["callback"],
            file_path=result.video_path,
            file_type="video"
        )

        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=caption,
            reply_markup=builder.as_markup()
        )

        # Clean up input images
        for img_path in kling_effect_images:
            cleanup_temp_file(img_path)

        await progress_msg.delete()
    else:
        # Clean up input images
        for img_path in kling_effect_images:
            cleanup_temp_file(img_path)

        try:
            await progress_msg.edit_text(f"❌ Ошибка: {result.error}", parse_mode=None)
        except Exception:
            pass

    await state.clear()


# ======================
# FSM HANDLERS - IMAGE GENERATION
# ======================

@router.message(MediaState.waiting_for_image_prompt, F.photo)
async def process_image_photo(message: Message, state: FSMContext, user: User):
    """Handle photo for image-to-image generation (supports multiple photos for multi-image generation)."""
    data = await state.get_data()
    service_name = data.get("service", "nano_banana")
    multi_images_count = data.get("multi_images_count", 0)

    # Download the photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    # Create temp path
    temp_path = get_temp_file_path(prefix="image_input", suffix=".jpg")

    await message.bot.download_file(file.file_path, temp_path)

    # Resize image if needed (before sending to API)
    resize_image_if_needed(str(temp_path), max_size_mb=2.0, max_dimension=2048)

    # Check if we're in multi-image mode
    if multi_images_count > 0:
        # Multi-image mode: add photo to list
        reference_image_paths = data.get("reference_image_paths", [])
        reference_image_paths.append(str(temp_path))
        await state.update_data(reference_image_paths=reference_image_paths)

        photos_count = len(reference_image_paths)
        service_display = {
            "nano_banana": "Nano Banana",
            "dalle": "DALL-E",
            "seedream": "Seedream 4.5",
            "gemini_image": "Gemini",
            "recraft": "Recraft",
            "kling_image": "Kling AI"
        }.get(service_name, service_name)

        # Check if photo has caption (description) - if yes, process immediately
        if message.caption and message.caption.strip():
            await state.update_data(photo_caption_prompt=message.caption.strip())

            # Route to appropriate image service
            if service_name == "nano_banana":
                await process_nano_image(message, user, state)
            elif service_name == "dalle":
                await process_dalle_image(message, user, state)
            elif service_name == "seedream":
                await process_seedream_image(message, user, state)
            elif service_name == "recraft":
                await process_recraft_image(message, user, state)
            elif service_name == "gemini_image":
                await process_gemini_image(message, user, state)
            elif service_name == "kling_image":
                await process_kling_image(message, user, state)
        else:
            # No caption - show status and ask for more photos or prompt
            await message.answer(
                f"✅ Фото {photos_count} сохранено!\n\n"
                f"📸 Вы можете:\n"
                f"• Загрузить ещё фото (всего: {photos_count}/{multi_images_count}+)\n"
                f"• Отправить текстовый промпт для начала генерации\n\n"
                f"**Примеры промптов для {service_display}:**\n"
                "• \"Создай портрет каждого в стиле аниме\"\n"
                "• \"Сделай разные варианты этой сцены\"\n"
                "• \"Примени этот стиль к каждому фото\""
            )
    else:
        # Single-image mode (backward compatibility)
        # Clean up old reference image if exists
        old_reference_path = data.get("reference_image_path")
        if old_reference_path:
            cleanup_temp_file(old_reference_path)

        # Save NEW image path to state
        await state.update_data(reference_image_path=str(temp_path))

        service_display = {
            "nano_banana": "Nano Banana",
            "dalle": "DALL-E",
            "seedream": "Seedream 4.5",
            "gemini_image": "Gemini",
            "recraft": "Recraft",
            "kling_image": "Kling AI"
        }.get(service_name, service_name)

        # Check if photo has caption (description)
        if message.caption and message.caption.strip():
            # User sent photo with description - process immediately
            # Save caption as prompt in state
            await state.update_data(photo_caption_prompt=message.caption.strip())

            # Route to appropriate image service
            if service_name == "dalle":
                await process_dalle_image(message, user, state)
            elif service_name == "gemini_image":
                await process_gemini_image(message, user, state)
            elif service_name == "nano_banana":
                await process_nano_image(message, user, state)
            elif service_name == "seedream":
                await process_seedream_image(message, user, state)
            elif service_name == "recraft":
                await process_recraft_image(message, user, state)
            elif service_name == "kling_image":
                await process_kling_image(message, user, state)
        else:
            # No caption - ask for description
            await message.answer(
                f"✅ Фото получено!\n\n"
                f"📝 Теперь отправьте описание изображения, которое вы хотите создать на основе этого фото.\n\n"
                f"**Примеры для {service_display}:**\n"
                "• \"Сделай в стиле аниме\"\n"
                "• \"Преобразуй в акварельный рисунок\"\n"
                "• \"Сделай фон космическим\"\n"
                "• \"Преобразуй в стиль Ван Гога\""
            )


@router.message(MediaState.waiting_for_image_prompt, F.text)
async def process_image_prompt(message: Message, state: FSMContext, user: User):
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    # Check message length (max 2000 characters)
    if message.text and len(message.text) > 2000:
        await message.answer(
            "⚠️ Описание слишком длинное!\n\n"
            f"Максимальная длина: 2000 символов\n"
            f"Ваше описание: {len(message.text)} символов\n\n"
            "Пожалуйста, сократите описание и попробуйте снова."
        )
        return

    data = await state.get_data()
    service_name = data.get("service", "dalle")

    if service_name == "dalle":
        await process_dalle_image(message, user, state)
    elif service_name == "gemini_image":
        await process_gemini_image(message, user, state)
    elif service_name == "nano_banana":
        await process_nano_image(message, user, state)
    elif service_name == "kling_image":
        await process_kling_image(message, user, state)
    elif service_name == "recraft":
        await process_recraft_image(message, user, state)
    elif service_name == "seedream":
        await process_seedream_image(message, user, state)
    elif service_name == "midjourney":
        await process_midjourney_image(message, user, state)
    else:
        await message.answer(
            f"Функция генерации изображений находится в разработке.\n"
            f"Ваш запрос получен: {message.text[:100]}..."
        )
        await state.clear()


async def process_dalle_image(message: Message, user: User, state: FSMContext):
    """Process DALL-E image generation or variation."""
    # Get state data (check if reference image was provided)
    data = await state.get_data()

    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    reference_image_path = data.get("reference_image_path", None)

    # Check and use tokens
    dalle_billing = get_image_model_billing("dalle3")
    estimated_tokens = dalle_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Clean up reference image if exists
            if reference_image_path:
                cleanup_temp_file(reference_image_path)

            await message.answer(
                f"❌ Недостаточно токенов для генерации изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Create service
    dalle_service = DalleService()

    # Determine operation mode
    if reference_image_path:
        # Image variation mode (DALL-E 2 only)
        progress_msg = await message.answer("🎨 Создаю вариацию изображения с DALL-E 2...")

        # Progress callback
        async def update_progress(text: str):
            try:
                await progress_msg.edit_text(text, parse_mode=None)
            except Exception:
                pass

        # Create variation
        result = await dalle_service.create_variation(
            image_path=reference_image_path,
            progress_callback=update_progress,
            model="dall-e-2",
            size="1024x1024"
        )
    else:
        # Text-to-image mode
        progress_msg = await message.answer("🎨 Генерирую изображение с DALL-E 3...")

        # Progress callback
        async def update_progress(text: str):
            try:
                await progress_msg.edit_text(text, parse_mode=None)
            except Exception:
                pass

        # Generate image
        result = await dalle_service.generate_image(
            prompt=prompt,
            progress_callback=update_progress,
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            style="vivid"
        )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Build caption in unified format
        image_type = "изображение" if not reference_image_path else "вариацию изображения"
        model_name = "DALL·E 3" if not reference_image_path else "DALL·E 2"

        caption_text = format_generation_message(
            content_type=image_type,
            model_name=model_name,
            tokens_used=tokens_used,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["gpt_image"]["text"],
            action_callback=MODEL_ACTIONS["gpt_image"]["callback"],
            file_path=result.image_path,
            file_type="image"
        )

        # Send image
        image_file = FSInputFile(result.image_path)
        await message.answer_photo(
            photo=image_file,
            caption=caption_text,
            reply_markup=builder.as_markup()
        )

        # Clean up
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("image_cleanup_failed", error=str(e))

        # Clean up reference image if exists
        if reference_image_path:
            cleanup_temp_file(reference_image_path)

        await progress_msg.delete()
    else:
        # Clean up reference image if exists
        if reference_image_path:
            cleanup_temp_file(reference_image_path)

        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    # Clear state after generation (success or failure)
    await state.clear()


async def process_gemini_image(message: Message, user: User, state: FSMContext):
    """Process Gemini/Imagen image generation."""
    # Get state data
    data = await state.get_data()
    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text

    # Check and use tokens
    gemini_billing = get_image_model_billing("nano-banana-image")
    estimated_tokens = gemini_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для генерации изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("🎨 Генерирую изображение...")

    # Create service
    gemini_service = GeminiImageService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate image
    result = await gemini_service.generate_image(
        prompt=prompt,
        progress_callback=update_progress,
        aspect_ratio="1:1"
    )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        # Send image
        image_file = FSInputFile(result.image_path)
        await message.answer_photo(
            photo=image_file,
            caption=f"✅ Изображение готово!\n\n"
                    f"Промпт: {prompt[:200]}\n"
                    f"Использовано токенов: {tokens_used:,}"
        )

        # Clean up
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("image_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


async def process_nano_image(message: Message, user: User, state: FSMContext):
    """Process Nano Banana (Gemini 2.5 Flash Image or Gemini 3 Pro Image) image generation.

    Supports both single and multiple image generation modes.
    """
    data = await state.get_data()

    prompt = data.get("photo_caption_prompt") or message.text
    reference_image_path = data.get("reference_image_path", None)
    reference_image_paths = data.get("reference_image_paths", [])
    multi_images_count = data.get("multi_images_count", 0)
    nano_is_pro = data.get("nano_is_pro", False)
    aspect_ratio = data.get("nano_aspect_ratio", "auto")

    # Select model based on PRO flag
    model = "gemini-3-pro-image-preview" if nano_is_pro else "gemini-2.5-flash-image"

    # Determine generation count
    if multi_images_count > 0:
        # Multi-image mode
        images_to_generate = multi_images_count
    else:
        # Single-image mode (backward compatibility)
        images_to_generate = 1

    # Calculate cost
    nano_billing_id = "banana-pro" if nano_is_pro else "nano-banana-image"
    cost_per_image = get_image_model_billing(nano_billing_id).tokens_per_generation
    estimated_tokens = cost_per_image * images_to_generate

    # Check and reserve tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Cleanup any reference images
            if reference_image_path:
                cleanup_temp_file(reference_image_path)
            for ref_path in reference_image_paths:
                cleanup_temp_file(ref_path)

            await message.answer(
                f"❌ Недостаточно токенов для генерации изображений!\n\n"
                f"Требуется: {estimated_tokens:,} токенов ({images_to_generate} × {cost_per_image:,})\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Progress message
    model_display = "Nano Banana PRO (Gemini 3)" if nano_is_pro else "Nano Banana (Gemini 2.5)"

    if images_to_generate > 1:
        # Multi-image mode
        progress_msg = await message.answer(
            f"🍌 Генерирую {images_to_generate} изображений с {model_display}...\n"
            f"⏳ Пожалуйста, подождите..."
        )
    else:
        # Single-image mode
        mode_text = "image-to-image" if (reference_image_path or reference_image_paths) else "text-to-image"
        progress_msg = await message.answer(
            f"🍌 Генерирую изображение с {model_display} ({mode_text})..."
        )

    nano_service = NanoBananaService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate images
    if images_to_generate > 1:
        # Multi-image generation mode: create multiple images in parallel
        import asyncio
        import re

        def create_unique_prompts(base_prompt: str, count: int) -> list[str]:
            """Create unique prompts for each image to ensure variety.

            Analyzes the prompt and creates variations for each generation.
            """
            # Check if prompt contains numbered scenes or variations
            # Pattern: "1. scene1, 2. scene2, 3. scene3" or "scene1, scene2, scene3"

            # Try to detect numbered list (handles multi-line scenes with commas)
            # Pattern: "1. scene text\n2. next scene" or "1) scene, more details\n2) next"
            numbered_pattern = r'(\d+)[\.\)]\s*(.*?)(?=\n\s*\d+[\.\)]|\Z)'
            numbered_matches = re.findall(numbered_pattern, base_prompt, re.MULTILINE | re.DOTALL)

            if numbered_matches and len(numbered_matches) >= count:
                # Extract base context (text before first numbered item)
                first_num_pos = re.search(r'\d+[\.\)]', base_prompt)
                base_context = base_prompt[:first_num_pos.start()].strip() if first_num_pos else ""

                # Define radically different camera and lighting setups for each scene
                # This forces variation even when user prompts are similar
                camera_setups = [
                    "Camera: Wide angle (24mm), natural soft daylight, centered composition, eye-level perspective",
                    "Camera: Macro lens (100mm), shallow depth of field, soft diffused backlight, 45-degree angle",
                    "Camera: Top-down view (bird's eye), dramatic side lighting with shadows, overhead perspective",
                    "Camera: Medium telephoto (85mm), three-quarter view, warm golden hour lighting, slightly tilted",
                    "Camera: Extreme close-up macro, bokeh background, bright key light from left, Dutch angle tilt",
                    "Camera: Ultra-wide angle (16mm), low angle looking up, cool morning light, dynamic composition",
                    "Camera: Standard lens (50mm), straight-on frontal view, high-key lighting, perfectly centered",
                    "Camera: Telephoto zoom (135mm), compressed perspective, backlit rim lighting, diagonal framing",
                    "Camera: Fish-eye lens, distorted perspective, colorful accent lighting, off-center placement",
                    "Camera: Tilt-shift lens, selective focus plane, sunset warm tones, asymmetric balance"
                ]

                # Use numbered scenes directly
                prompts = []
                for idx, (num, scene_text) in enumerate(numbered_matches[:count], 1):
                    scene = scene_text.strip()

                    # Get specific camera setup for this scene
                    camera_setup = camera_setups[idx % len(camera_setups)]

                    # Add strong technical specifications to force variation
                    technical_spec = (
                        f"\n\n[TECHNICAL REQUIREMENTS - Scene {idx}/{count}]:\n"
                        f"{camera_setup}\n"
                        f"CRITICAL: This scene MUST be visually DISTINCT from all other scenes. "
                        f"Different angle, different lighting direction, different composition style. "
                        f"Ignore any repetitive patterns from other scenes."
                    )

                    # Combine base context with specific scene
                    if base_context:
                        full_prompt = f"{base_context}. {scene}{technical_spec}"
                    else:
                        full_prompt = f"{scene}{technical_spec}"
                    prompts.append(full_prompt)
                return prompts

            # Try to detect comma-separated scenes (if more than 2 commas)
            comma_parts = [p.strip() for p in base_prompt.split(',') if p.strip()]
            if len(comma_parts) >= count:
                # Use comma-separated parts as separate scenes
                return comma_parts[:count]

            # Detect keywords that suggest multiple scenes
            scene_keywords = ['на кафеле', 'на ванной', 'лежит', 'стоит', 'рядом', 'держит', 'льется']
            detected_scenes = []

            # Split by common separators
            separators = ['. ', ', ', '; ']
            parts = [base_prompt]
            for sep in separators:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(sep))
                parts = new_parts

            # Extract scene descriptions
            for part in parts:
                part = part.strip()
                if any(keyword in part.lower() for keyword in scene_keywords):
                    detected_scenes.append(part)

            if detected_scenes and len(detected_scenes) >= count:
                # Use detected scenes
                base_instructions = base_prompt.split('.')[0] if '.' in base_prompt else ""
                prompts = []
                for scene in detected_scenes[:count]:
                    if base_instructions:
                        prompts.append(f"{base_instructions}. {scene}")
                    else:
                        prompts.append(scene)
                return prompts

            # Fallback: create variations by adding diversity instructions
            variations = []
            variation_angles = [
                "top-down aerial view with dramatic overhead lighting",
                "low angle close-up with shallow depth of field",
                "45-degree side angle with natural soft lighting",
                "extreme macro detail shot with bokeh background",
                "wide environmental shot showing full context",
                "dramatic side lighting with strong shadows",
                "backlit silhouette with rim lighting",
                "Dutch angle (tilted) perspective for dynamic feel",
                "straight-on centered composition with symmetry",
                "diagonal composition with leading lines"
            ]

            for i in range(count):
                angle_instruction = variation_angles[i % len(variation_angles)]
                variation = (
                    f"{base_prompt}\n\n"
                    f"VARIATION {i+1}: Use {angle_instruction}. "
                    f"Make this COMPLETELY DIFFERENT from other variations. "
                    f"UNIQUE angle, DIFFERENT background, DISTINCT atmosphere."
                )
                variations.append(variation)

            return variations

        # Create unique prompts for each image
        unique_prompts = create_unique_prompts(prompt, images_to_generate)

        # Log unique prompts for debugging
        logger.info(
            "nano_multi_prompts_created",
            count=len(unique_prompts),
            original_prompt=prompt[:200],
            prompts_lengths=[len(p) for p in unique_prompts],
            prompts_preview=[p[:300] for p in unique_prompts]
        )

        # Log each prompt separately for better visibility
        for idx, up in enumerate(unique_prompts, 1):
            logger.info(
                "nano_multi_prompt_detail",
                scene_index=idx,
                prompt_length=len(up),
                prompt_start=up[:400]
            )

        async def generate_single_image(index: int, image_prompt: str, ref_image: str = None):
            """Generate a single image with unique prompt."""
            try:
                result = await nano_service.generate_image(
                    prompt=image_prompt,
                    model=model,
                    progress_callback=None,  # Disable individual progress for parallel generation
                    aspect_ratio=aspect_ratio,
                    reference_image_path=ref_image
                )
                return (index, result, ref_image)
            except Exception as e:
                logger.error("nano_multi_image_generation_failed", index=index, error=str(e))
                return (index, None, ref_image)

        # Update progress: generating
        await update_progress(
            f"🍌 Генерирую {images_to_generate} изображений параллельно...\n"
            f"⏳ Это может занять 30-60 секунд..."
        )

        # Create tasks for parallel generation
        # Use reference image for ALL generations to maintain consistent product design
        tasks = []
        if reference_image_paths:
            # Use same reference for all images to keep bottle/product identical
            ref_path = reference_image_paths[0]
            for idx in range(images_to_generate):
                task_prompt = unique_prompts[idx] if idx < len(unique_prompts) else prompt
                tasks.append(generate_single_image(idx, task_prompt, ref_path))
        else:
            # No reference images: generate all as text-to-image with unique prompts
            for idx in range(images_to_generate):
                task_prompt = unique_prompts[idx] if idx < len(unique_prompts) else prompt
                tasks.append(generate_single_image(idx, task_prompt, None))

        # Execute all tasks in parallel
        results_with_indices = await asyncio.gather(*tasks)

        # Process results
        successful_results = []
        failed_count = 0

        for idx, result, ref_path in results_with_indices:
            if result and result.success:
                successful_results.append((idx, result))
            else:
                failed_count += 1
                logger.warning("nano_multi_image_failed", index=idx, error=result.error if result else "Unknown error")

        # Cleanup reference images
        for ref_path in reference_image_paths:
            cleanup_temp_file(ref_path)

        # Send results
        if successful_results:
            await update_progress(
                f"✅ Готово: {len(successful_results)}/{images_to_generate} изображений\n"
                f"📤 Отправляю результаты..."
            )

            total_tokens_used = sum(r.metadata.get("tokens_used", cost_per_image) for _, r in successful_results)

            async with async_session_maker() as session:
                sub_service = SubscriptionService(session)
                user_tokens = await sub_service.get_available_tokens(user.id)

            # Send summary message first
            model_name = "Nano Banana PRO (Gemini 3)" if nano_is_pro else "Nano Banana (Gemini 2.5)"
            summary_text = (
                f"✅ **Генерация завершена!**\n\n"
                f"🍌 Модель: {model_name}\n"
                f"🎨 Создано изображений: {len(successful_results)}/{images_to_generate}\n"
                f"💰 Использовано токенов: {total_tokens_used:,}\n"
                f"💎 Осталось токенов: {user_tokens:,}\n\n"
                f"📝 Промпт: {prompt[:150]}{'...' if len(prompt) > 150 else ''}"
            )

            if failed_count > 0:
                summary_text += f"\n\n⚠️ Не удалось создать: {failed_count} изображений"

            await message.answer(summary_text, parse_mode="Markdown")

            # Send each image individually
            nano_callback = "bot.nano_pro" if nano_is_pro else "bot.nano"
            for idx, result in successful_results:
                try:
                    image_file = FSInputFile(result.image_path)
                    builder = create_action_keyboard(
                        action_text=MODEL_ACTIONS["nano_banana"]["text"],
                        action_callback=nano_callback,
                        file_path=result.image_path,
                        file_type="image"
                    )
                    await message.answer_photo(
                        photo=image_file,
                        caption=f"🖼 Изображение {idx + 1}/{images_to_generate}",
                        reply_markup=builder.as_markup()
                    )
                except Exception as send_error:
                    logger.error("nano_multi_image_send_failed", index=idx, error=str(send_error))

            await progress_msg.delete()
        else:
            # All failed
            for ref_path in reference_image_paths:
                cleanup_temp_file(ref_path)

            await progress_msg.edit_text(
                f"❌ Не удалось создать ни одного изображения.\n"
                f"Попробуйте изменить промпт или параметры.",
                parse_mode=None
            )

        await state.clear()
        return

    # Single-image generation mode (original code)
    result = await nano_service.generate_image(
        prompt=prompt,
        model=model,
        progress_callback=update_progress,
        aspect_ratio=aspect_ratio,
        reference_image_path=reference_image_path or (reference_image_paths[0] if reference_image_paths else None)
    )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        model_name = "Nano Banana PRO (Gemini 3)" if nano_is_pro else "Nano Banana (Gemini 2.5)"
        info_text = format_generation_message(
            content_type=CONTENT_TYPES["image"],
            model_name=model_name,
            tokens_used=tokens_used,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Create action keyboard - use correct callback based on PRO mode
        nano_callback = "bot.nano_pro" if nano_is_pro else "bot.nano"
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["nano_banana"]["text"],
            action_callback=nano_callback,
            file_path=result.image_path,
            file_type="image"
        )

        try:
            file_size = os.path.getsize(result.image_path)
            logger.info("nano_image_file_size", path=result.image_path, size=file_size)

            if file_size > 2 * 1024 * 1024:
                logger.info("nano_image_optimizing", original_size=file_size)

                img = Image.open(result.image_path)

                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img,
                        mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85, optimize=True)
                buffer.seek(0)

                photo = BufferedInputFile(buffer.read(), filename="image.jpg")
                await message.answer_photo(
                    photo=photo,
                    caption=info_text,
                    reply_markup=builder.as_markup()
                )
            else:
                try:
                    image_file = FSInputFile(result.image_path)
                    await message.answer_photo(
                        photo=image_file,
                        caption=info_text,
                        reply_markup=builder.as_markup()
                    )
                except Exception:
                    img = Image.open(result.image_path)

                    if img.mode in ("RGBA", "LA", "P"):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(
                            img,
                            mask=img.split()[-1] if img.mode == "RGBA" else None
                        )
                        img = background

                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=90, optimize=True)
                    buffer.seek(0)

                    photo = BufferedInputFile(buffer.read(), filename="image.jpg")
                    await message.answer_photo(
                        photo=photo,
                        caption=info_text,
                        reply_markup=builder.as_markup()
                    )

        except Exception as send_error:
            logger.error("nano_image_send_failed", error=str(send_error))
            try:
                doc_file = FSInputFile(result.image_path)
                await message.answer_document(
                    document=doc_file,
                    caption=info_text,
                    reply_markup=builder.as_markup()
                )
            except Exception as doc_error:
                logger.error("nano_image_send_as_document_failed", error=str(doc_error))
                await message.answer(
                    info_text,
                    reply_markup=builder.as_markup()
                )

        # Cleanup
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("nano_image_cleanup_failed", error=str(e))

        # Cleanup reference images (both single and multiple)
        if reference_image_path:
            cleanup_temp_file(reference_image_path)
        for ref_path in reference_image_paths:
            cleanup_temp_file(ref_path)

        await progress_msg.delete()

    else:
        # Cleanup reference images on failure
        if reference_image_path:
            cleanup_temp_file(reference_image_path)
        for ref_path in reference_image_paths:
            cleanup_temp_file(ref_path)

        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            pass

    # Clear state after generation (success or failure)
    await state.clear()


async def process_kling_image(message: Message, user: User, state: FSMContext):
    """Process Kling AI image generation."""
    data = await state.get_data()

    # Get settings from FSM state
    kling_image_settings = KlingImageSettings.from_dict(data)

    prompt = data.get("photo_caption_prompt") or message.text
    reference_image_path = data.get("reference_image_path", None)

    # Auto-translate if enabled
    if kling_image_settings.auto_translate and prompt:
        from app.services.ai.openai_service import OpenAIService
        try:
            openai_service = OpenAIService()
            translated = await openai_service.translate_to_english(prompt)
            if translated:
                prompt = translated
        except Exception as e:
            logger.warning("kling_image_translate_failed", error=str(e))

    kling_image_billing = get_image_model_billing("kling-image")
    estimated_tokens = kling_image_billing.tokens_per_generation

    # Check and reserve tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            if reference_image_path:
                cleanup_temp_file(reference_image_path)

            await message.answer(
                f"❌ Недостаточно токенов для генерации изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Progress message
    mode_text = "image-to-image" if reference_image_path else "text-to-image"
    model_names = {"kling-v1": "v1", "kling-v1-5": "v1.5", "kling-v2": "v2"}
    model_display = model_names.get(kling_image_settings.model, kling_image_settings.model)
    progress_msg = await message.answer(
        f"🎞 Генерирую изображение с Kling AI {model_display} ({mode_text})..."
    )

    kling_service = KlingImageService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate image with user settings
    result = await kling_service.generate_image(
        prompt=prompt,
        model=kling_image_settings.model,
        progress_callback=update_progress,
        aspect_ratio=kling_image_settings.aspect_ratio,
        resolution=kling_image_settings.resolution,
        image_path=reference_image_path  # For image-to-image mode (None for text-to-image)
    )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        info_text = format_generation_message(
            content_type=CONTENT_TYPES["image"],
            model_name="Kling AI",
            mode="text-to-image" if not reference_image_path else "image-to-image",
            tokens_used=tokens_used,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text="🎞 Создать новое изображение",
            action_callback="bot.kling_image",
            file_path=result.image_path,
            file_type="image"
        )

        try:
            photo = FSInputFile(result.image_path)
            await message.answer_photo(
                photo=photo,
                caption=info_text,
                reply_markup=builder.as_markup()
            )

        except Exception as send_error:
            logger.error("kling_image_send_failed", error=str(send_error))
            try:
                doc_file = FSInputFile(result.image_path)
                await message.answer_document(
                    document=doc_file,
                    caption=info_text,
                    reply_markup=builder.as_markup()
                )
            except Exception as doc_error:
                logger.error("kling_image_send_as_document_failed", error=str(doc_error))
                await message.answer(
                    info_text,
                    reply_markup=builder.as_markup()
                )

        # Cleanup
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("kling_image_cleanup_failed", error=str(e))

        if reference_image_path:
            cleanup_temp_file(reference_image_path)

        await progress_msg.delete()

    else:
        if reference_image_path:
            cleanup_temp_file(reference_image_path)

        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            pass

    await state.clear()


async def process_recraft_image(message: Message, user: User, state: FSMContext):
    """Process Recraft AI image generation."""
    data = await state.get_data()
    prompt = data.get("photo_caption_prompt") or message.text

    recraft_billing = get_image_model_billing("recraft")
    estimated_tokens = recraft_billing.tokens_per_generation

    # Check and reserve tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для генерации изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Progress message
    progress_msg = await message.answer(
        "🎨 Генерирую изображение с Recraft AI..."
    )

    recraft_service = RecraftService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate image
    result = await recraft_service.generate_image(
        prompt=prompt,
        progress_callback=update_progress,
        model="recraftv2",  # Use V2 for better price
        style="realistic_image",  # Default style
        size="1024x1024"
    )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        info_text = format_generation_message(
            content_type=CONTENT_TYPES["image"],
            model_name="Recraft AI",
            tokens_used=tokens_used,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text="🎨 Создать новое изображение",
            action_callback="bot.recraft",
            file_path=result.image_path,
            file_type="image"
        )

        try:
            photo = FSInputFile(result.image_path)
            await message.answer_photo(
                photo=photo,
                caption=info_text,
                reply_markup=builder.as_markup()
            )

        except Exception as send_error:
            logger.error("recraft_image_send_failed", error=str(send_error))
            try:
                doc_file = FSInputFile(result.image_path)
                await message.answer_document(
                    document=doc_file,
                    caption=info_text,
                    reply_markup=builder.as_markup()
                )
            except Exception as doc_error:
                logger.error("recraft_image_send_as_document_failed", error=str(doc_error))
                await message.answer(
                    info_text,
                    reply_markup=builder.as_markup()
                )

        # Cleanup
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("recraft_image_cleanup_failed", error=str(e))

        await progress_msg.delete()
        await state.update_data(photo_caption_prompt=None)

    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            pass

    # Don't clear state - keep service so user can generate more images
    await state.update_data(photo_caption_prompt=None)


# ======================
# FSM HANDLERS - AUDIO
# ======================

@router.message(MediaState.waiting_for_audio_prompt, F.text)
async def process_audio_prompt(message: Message, state: FSMContext, user: User):
    # CRITICAL FIX: Ignore commands (text starting with /)
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    data = await state.get_data()
    service_name = data.get("service", "suno")

    if service_name == "suno":
        await process_suno_audio(message, user, state)
    elif service_name == "tts":
        await process_tts_audio(message, user, state)
    else:
        display = {
            "suno": "Suno AI",
            "tts": "OpenAI TTS"
        }.get(service_name, service_name)

        await message.answer(
            f"Функция генерации аудио ({display}) находится в разработке.\n"
            f"Ваш текст получен: {message.text[:100]}..."
        )
        await state.clear()


async def process_suno_audio(message: Message, user: User, state: FSMContext):
    """Process Suno AI music generation."""
    prompt = message.text

    # Check and use tokens
    estimated_tokens = 5000  # Suno AI cost

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для генерации музыки!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("🎵 Начинаю создание музыки с Suno AI...")

    # Create service
    suno_service = SunoService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate music
    result = await suno_service.generate_audio(
        prompt=prompt,
        progress_callback=update_progress
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate unified notification message
        caption = format_generation_message(
            content_type=CONTENT_TYPES["audio"],
            model_name="Suno AI",
            tokens_used=estimated_tokens,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Send audio
        audio_file = FSInputFile(result.audio_path)
        await message.answer_audio(
            audio=audio_file,
            caption=caption,
            title=f"Suno AI - {prompt[:50]}"
        )

        # Clean up
        try:
            pass  # os.remove(result.audio_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("suno_audio_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации музыки:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


# ======================
# FSM HANDLERS - IMAGE PROCESSING
# ======================

@router.message(MediaState.waiting_for_replace_bg_image, F.photo)
async def process_replace_bg_image(message: Message, state: FSMContext, user: User):
    """Process image for background replacement."""
    # Get the largest photo
    photo = message.photo[-1]

    # Download photo
    file = await message.bot.get_file(photo.file_id)
    temp_path = get_temp_file_path(prefix="replace_bg", suffix=".jpg", user_id=user.id)
    await message.bot.download_file(file.file_path, temp_path)

    # Resize if needed
    temp_path = resize_image_if_needed(temp_path, max_size_mb=3.0, max_dimension=2048)

    # Save to state
    await state.update_data(replace_bg_image_path=str(temp_path))

    # Ask for background description
    await message.answer(
        "✅ Изображение получено!\n\n"
        "📝 Теперь опишите новый фон:\n\n"
        "**Примеры:**\n"
        "• \"Белый фон\"\n"
        "• \"Пляж с пальмами на закате\"\n"
        "• \"Городская улица ночью\"\n"
        "• \"Абстрактный градиент от синего к фиолетовому\"",
        parse_mode="Markdown"
    )

    await state.set_state(MediaState.waiting_for_replace_bg_prompt)


@router.message(MediaState.waiting_for_replace_bg_prompt, F.text)
async def process_replace_bg_prompt(message: Message, state: FSMContext, user: User):
    """Process background replacement with new background description."""
    # CRITICAL FIX: Ignore commands
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    data = await state.get_data()
    image_path = data.get("replace_bg_image_path")
    background_description = message.text.strip()

    if not image_path:
        await message.answer("❌ Изображение не найдено. Начните заново с /start")
        await state.clear()
        return

    # Check tokens
    estimated_tokens = 2000

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            cleanup_temp_file(image_path)
            await message.answer(
                f"❌ Недостаточно токенов для замены фона!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("🎨 Заменяю фон...")

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Use Nano Banana service with image-to-image
    nano_service = NanoBananaService()

    # Create prompt for background replacement
    prompt = f"Замени фон на этом изображении на: {background_description}. Сохрани основной объект, но полностью замени фон."

    # Generate with reference image
    result = await nano_service.generate_image(
        prompt=prompt,
        reference_image_path=image_path,
        progress_callback=update_progress
    )

    # Clean up original image
    cleanup_temp_file(image_path)

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate caption
        caption = format_generation_message(
            content_type=CONTENT_TYPES["image"],
            model_name="Замена фона (Gemini 2.5 Flash)",
            tokens_used=estimated_tokens,
            user_tokens=user_tokens,
            prompt=background_description,
            mode="background-replacement"
        )

        # Send image
        await message.answer_photo(
            photo=FSInputFile(result.image_path),
            caption=caption,
            reply_markup=create_action_keyboard(
                action_text="🔄 Заменить фон еще раз",
                action_callback="bot.pi_repb",
                file_path=result.image_path,
                file_type="image"
            ).as_markup()
        )

        await progress_msg.delete()

        # Clean up generated image
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("replace_bg_cleanup_failed", error=str(e))

        logger.info(
            "replace_bg_completed",
            user_id=user.id,
            background=background_description[:50],
            tokens=estimated_tokens
        )
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка замены фона:\n{result.error}"
            )
        except Exception:
            pass

        logger.error("replace_bg_failed", user_id=user.id, error=result.error)

    await state.clear()


@router.message(MediaState.waiting_for_image, F.photo)
async def process_image(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    service = data.get("service", "remove_bg")

    display = {
        "remove_bg": "Удаление фона",
        "replace_bg": "Замена фона"
    }.get(service, service)

    await message.answer(
        f"Функция обработки изображений ({display}) находится в разработке.\n"
        "Изображение получено!"
    )
    await state.clear()


@router.message(MediaState.waiting_for_upscale_image, F.photo)
async def process_upscale(message: Message, state: FSMContext, user: User):
    """Process image upscaling."""
    # Get the largest photo
    photo = message.photo[-1]

    # Check and use tokens
    estimated_tokens = 2000

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для улучшения изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("📥 Загружаю изображение...")

    # Download photo
    file = await message.bot.get_file(photo.file_id)

    # Create temp path
    temp_path = get_temp_file_path(prefix="upscale", suffix=".jpg")

    await message.bot.download_file(file.file_path, temp_path)

    # Create service
    stability_service = StabilityService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Upscale image
    result = await stability_service.upscale_image(
        image_path=str(temp_path),
        scale_factor=2,
        progress_callback=update_progress
    )

    # Clean up temp file
    cleanup_temp_file(temp_path)

    if result.success:

        # Send upscaled image
        upscaled_file = FSInputFile(result.image_path)
        await message.answer_photo(
            photo=upscaled_file,
            caption=f"✅ Изображение улучшено!\n\n"
                    f"Использовано токенов: {estimated_tokens:,}"
        )

        # Clean up
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("upscale_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка улучшения изображения:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


# ======================
# FSM HANDLERS - WHISPER (VOICE TRANSCRIPTION)
# ======================

@router.message(MediaState.waiting_for_whisper_audio, F.voice | F.audio)
async def process_whisper_audio(message: Message, state: FSMContext, user: User):
    """Process Whisper audio transcription."""

    # Check and use tokens
    estimated_tokens = 1000  # Whisper cost per minute

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для расшифровки аудио!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("📥 Загружаю аудио...")

    # Download audio
    if message.voice:
        file = await message.bot.get_file(message.voice.file_id)
        file_ext = "ogg"
    else:
        file = await message.bot.get_file(message.audio.file_id)
        file_ext = "mp3"

    # Create temp path
    temp_path = get_temp_file_path(prefix="audio", suffix=f".{file_ext}")

    await message.bot.download_file(file.file_path, temp_path)

    # Create service
    whisper_service = OpenAIAudioService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    await update_progress("🎙️ Расшифровываю аудио...")

    # Transcribe audio
    result = await whisper_service.transcribe(
        audio_path=str(temp_path),
        language="ru"  # Russian language
    )

    # Clean up temp file
    cleanup_temp_file(temp_path)

    if result.success:
        # Send transcription
        await message.answer(
            f"✅ **Расшифровка готова!**\n\n"
            f"📝 **Текст:**\n{result.text}\n\n"
            f"💰 Использовано токенов: {estimated_tokens:,}"
        )

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка расшифровки аудио:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


# ======================
# FSM HANDLERS - TTS UPDATE
# ======================

async def process_tts_audio(message: Message, user: User, state: FSMContext):
    """Process OpenAI TTS generation."""
    text = message.text

    if len(text) > 4096:
        await message.answer("❌ Текст слишком длинный! Максимум 4096 символов.")
        await state.clear()
        return

    # Check and use tokens
    estimated_tokens = 200  # TTS cost

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для озвучки текста!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("🎙️ Генерирую речь...")

    # Create service
    tts_service = OpenAIAudioService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate audio (default voice: alloy)
    result = await tts_service.generate_audio(
        prompt=text,
        voice="alloy",
        model="tts-1",
        progress_callback=update_progress
    )

    if result.success:
        # Send audio
        audio_file = FSInputFile(result.audio_path)
        await message.answer_audio(
            audio=audio_file,
            caption=f"✅ Озвучка готова!\n\n"
                    f"Голос: alloy\n"
                    f"Использовано токенов: {estimated_tokens:,}",
            title="OpenAI TTS"
        )

        # Clean up
        try:
            pass  # os.remove(result.audio_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("tts_audio_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации аудио:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


# ======================
# FSM HANDLERS - GPT VISION (IMAGE ANALYSIS)
# ======================

@router.message(MediaState.waiting_for_vision_image, F.photo)
async def process_vision_image(message: Message, state: FSMContext, user: User):
    """Receive image and ask for analysis prompt."""
    # Get the largest photo
    photo = message.photo[-1]

    # Send progress message
    progress_msg = await message.answer("📥 Загружаю изображение...")

    # Download photo
    file = await message.bot.get_file(photo.file_id)

    # Create temp path
    temp_path = get_temp_file_path(prefix="vision", suffix=".jpg")

    await message.bot.download_file(file.file_path, temp_path)

    # Store image path in state
    await state.update_data(image_path=str(temp_path))
    await state.set_state(MediaState.waiting_for_vision_prompt)

    await progress_msg.edit_text(
        "✅ Изображение получено!\n\n"
        "Теперь отправьте вопрос или задание для анализа изображения.\n\n"
        "**Примеры:**\n"
        "• Что изображено на этой картинке?\n"
        "• Опиши это изображение подробно\n"
        "• Какой текст есть на изображении?\n"
        "• Что за объекты изображены?"
    )


@router.message(MediaState.waiting_for_vision_prompt, F.text)
async def process_vision_prompt(message: Message, state: FSMContext, user: User):
    """Process GPT Vision image analysis."""
    data = await state.get_data()
    image_path = data.get("image_path")
    prompt = message.text

    if not image_path or not os.path.exists(image_path):
        await message.answer("❌ Ошибка: изображение не найдено. Попробуйте снова.")
        await state.clear()
        return

    # Check and use tokens
    estimated_tokens = 1000  # GPT-4 Vision cost

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для анализа изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            # Clean up temp file
            cleanup_temp_file(image_path)
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("👁 Анализирую изображение...")

    # Create service
    vision_service = VisionService()

    # Analyze image
    result = await vision_service.analyze_image(
        image_path=image_path,
        prompt=prompt,
        model="gpt-4o",
        max_tokens=1000,
        detail="auto"
    )

    # Clean up temp file
    cleanup_temp_file(image_path)

    if result.success:
        # Send analysis
        await message.answer(
            f"✅ **Анализ изображения готов!**\n\n"
            f"📝 **Ответ:**\n{result.content}\n\n"
            f"💰 Использовано токенов: {result.tokens_used:,}"
        )

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка анализа изображения:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


# ======================
# PHOTO TOOLS HANDLERS
# ======================

@router.message(MediaState.waiting_for_photo_upscale, F.photo)
async def process_photo_upscale(message: Message, state: FSMContext, user: User):
    """Process photo quality improvement using PIL image enhancement."""
    # Get the largest photo
    photo = message.photo[-1]

    # Check and use tokens (basic image processing is cheap)
    estimated_tokens = 500

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для улучшения изображения!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("📥 Загружаю изображение...")

    # Download photo
    file = await message.bot.get_file(photo.file_id)

    # Create temp path
    temp_path = get_temp_file_path(prefix="enhance", suffix=".jpg")

    await message.bot.download_file(file.file_path, temp_path)

    try:
        # Progress update
        await progress_msg.edit_text("🎨 Улучшаю качество изображения...", parse_mode=None)

        # Open image with PIL
        from PIL import Image, ImageEnhance, ImageFilter

        img = Image.open(temp_path)

        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background

        # 1. Enhance sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)  # Increase sharpness by 50%

        # 2. Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # Increase contrast by 20%

        # 3. Enhance color
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)  # Increase color saturation by 10%

        # 4. Enhance brightness slightly
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.05)  # Increase brightness by 5%

        # 5. Apply subtle unsharp mask for additional sharpness
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

        # Save enhanced image
        enhanced_path = get_temp_file_path(prefix="enhanced", suffix=".jpg")

        # Save with high quality
        img.save(str(enhanced_path), 'JPEG', quality=95, optimize=True)

        # Check file size and optimize if needed
        file_size = os.path.getsize(enhanced_path)
        max_size = 10 * 1024 * 1024  # 10 MB Telegram limit

        if file_size > max_size:
            logger.info("enhanced_image_too_large", size=file_size, max_size=max_size)
            # Reduce quality gradually until it fits
            quality = 90
            while file_size > max_size and quality > 60:
                img.save(str(enhanced_path), 'JPEG', quality=quality, optimize=True)
                file_size = os.path.getsize(enhanced_path)
                quality -= 5
                logger.info("enhanced_image_compressed", new_size=file_size, quality=quality)

        # Clean up original temp file
        cleanup_temp_file(temp_path)

        # Send enhanced image
        enhanced_file = FSInputFile(enhanced_path)
        await message.answer_photo(
            photo=enhanced_file,
            caption=f"✅ Изображение улучшено!\n\n"
                    f"Применены улучшения: резкость, контраст, цвета, яркость.\n\n"
                    f"Использовано токенов: {estimated_tokens:,}"
        )

        # Clean up enhanced file
        cleanup_temp_file(enhanced_path)

        await progress_msg.delete()

    except Exception as e:
        # Clean up temp files on error
        cleanup_temp_file(temp_path)

        logger.error("photo_quality_improvement_failed", error=str(e))

        try:
            from app.core.error_handlers import format_user_error
            user_message = format_user_error(e, provider="Image Enhancement", user_id=user.id)
            await progress_msg.edit_text(f"❌ {user_message}")
        except Exception:
            pass

    await state.clear()


@router.message(MediaState.waiting_for_photo_replace_bg, F.photo)
async def process_photo_replace_bg(message: Message, state: FSMContext, user: User):
    """Process background replacement."""
    # First, save the photo and ask for background description
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)

    # Download photo
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        await message.bot.download_file(file_info.file_path, tmp_file.name)
        image_path = tmp_file.name

    # Save to state
    await state.update_data(saved_image_path=image_path)

    # Ask for background description
    await message.answer(
        "📤 Фото получено!\n\n"
        "✏️ Теперь опишите, какой фон вы хотите:\n\n"
        "Примеры:\n"
        "• Горный пейзаж с заснеженными вершинами\n"
        "• Тропический пляж с пальмами\n"
        "• Современный офис\n"
        "• Космическое пространство с звездами",
        reply_markup=back_to_main_keyboard()
    )


@router.message(MediaState.waiting_for_photo_replace_bg, F.text)
async def process_photo_replace_bg_prompt(message: Message, state: FSMContext, user: User):
    """Process background replacement with Gemini (NanoBananaService)."""
    # CRITICAL FIX: Ignore commands
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    data = await state.get_data()
    image_path = data.get("saved_image_path")

    if not image_path or not os.path.exists(image_path):
        await message.answer("❌ Ошибка: фото не найдено. Попробуйте снова.")
        await state.clear()
        return

    bg_description = message.text

    # Check and use tokens (Gemini image-to-image)
    nano_billing = get_image_model_billing("nano-banana-image")
    estimated_tokens = nano_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для замены фона!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            # Clean up saved image
            cleanup_temp_file(image_path)
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("🎨 Заменяю фон с Gemini 2.5 Flash...")

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Use Nano Banana service with image-to-image
    nano_service = NanoBananaService()

    # Create prompt for background replacement
    prompt = f"Замени фон на этом изображении на: {bg_description}. Сохрани основной объект, но полностью замени фон."

    # Generate with reference image using Gemini 2.5 Flash Image
    result = await nano_service.generate_image(
        prompt=prompt,
        model="gemini-2.5-flash-image",
        reference_image_path=image_path,
        progress_callback=update_progress
    )

    # Clean up original image
    cleanup_temp_file(image_path)

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Generate caption
        caption = format_generation_message(
            content_type=CONTENT_TYPES["image"],
            model_name="Замена фона (Gemini 2.5 Flash)",
            tokens_used=estimated_tokens,
            user_tokens=user_tokens,
            prompt=bg_description,
            mode="background-replacement"
        )

        # Send image
        await message.answer_photo(
            photo=FSInputFile(result.image_path),
            caption=caption,
            reply_markup=create_action_keyboard(
                action_text="🔄 Заменить фон еще раз",
                action_callback="bot.pi_repb",
                file_path=result.image_path,
                file_type="image"
            ).as_markup()
        )

        await progress_msg.delete()

        # Clean up generated image
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("replace_bg_cleanup_failed", error=str(e))

        logger.info(
            "photo_replace_bg_completed",
            user_id=user.id,
            background=bg_description[:50],
            tokens=estimated_tokens
        )
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка замены фона:\n{result.error}"
            )
        except Exception:
            pass

        logger.error("photo_replace_bg_failed", user_id=user.id, error=result.error)

    await state.clear()


@router.message(MediaState.waiting_for_photo_remove_bg, F.photo)
async def process_photo_remove_bg(message: Message, state: FSMContext, user: User):
    """Process background removal using Remove.bg API."""
    # Get the largest photo
    photo = message.photo[-1]

    # Check and use tokens
    estimated_tokens = 1000

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для удаления фона!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("📥 Загружаю изображение...")

    # Download photo
    file = await message.bot.get_file(photo.file_id)

    # Create temp path
    temp_path = get_temp_file_path(prefix="removebg", suffix=".jpg")

    await message.bot.download_file(file.file_path, temp_path)

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Remove background
    removebg_service = RemoveBgService()
    result = await removebg_service.process_image(
        image_path=str(temp_path),
        progress_callback=update_progress,
        size="auto",  # auto, preview, full
        type="auto"   # auto, person, product, car
    )

    # Clean up temp file
    cleanup_temp_file(temp_path)

    if result.success:
        # Send image with removed background
        result_file = FSInputFile(result.image_path)

        # Try sending as photo first
        try:
            await message.answer_photo(
                photo=result_file,
                caption=f"✅ Фон удалён!\n\n"
                        f"Использовано токенов: {estimated_tokens:,}"
            )
        except Exception:
            # If photo fails (transparent images sometimes do), send as document
            await message.answer_document(
                document=result_file,
                caption=f"✅ Фон удалён!\n\n"
                        f"Изображение с прозрачным фоном (PNG).\n\n"
                        f"Использовано токенов: {estimated_tokens:,}"
            )

        # Clean up
        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception as e:
            logger.error("removebg_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка удаления фона:\n{result.error}"
            )
        except Exception:
            pass

    await state.clear()


@router.message(MediaState.waiting_for_photo_vectorize, F.photo)
async def process_photo_vectorize(message: Message, state: FSMContext, user: User):
    """Process photo vectorization."""
    await _process_photo_tool(
        message, state, user,
        tool_name="Векторизация",
        prompt=(
            "Analyze this image and describe how to convert it to a vector format. "
            "Provide recommendations for: tracing method, color palette reduction, "
            "path simplification, and optimal settings for this specific image type. "
            "Suggest the best vectorization approach (outline, centerline, or full color)."
        ),
        emoji="📐"
    )


async def _process_photo_tool(message: Message, state: FSMContext, user: User,
                              tool_name: str, prompt: str, emoji: str):
    """Helper function to process photo with GPT Vision."""
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)

    # Download photo
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        await message.bot.download_file(file_info.file_path, tmp_file.name)
        image_path = tmp_file.name

    await _process_photo_with_path(message, state, user, image_path, tool_name, prompt, emoji)


async def _process_photo_with_path(message: Message, state: FSMContext, user: User,
                                   image_path: str, tool_name: str, prompt: str, emoji: str):
    """Process photo with given path."""
    # Check and use tokens
    estimated_tokens = 1500  # GPT-4 Vision cost

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для обработки фото!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            # Clean up temp file
            cleanup_temp_file(image_path)
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer(f"{emoji} Анализирую фото...")

    # Create service
    vision_service = VisionService()

    # Analyze image
    result = await vision_service.analyze_image(
        image_path=image_path,
        prompt=prompt,
        model="gpt-4o",
        max_tokens=1500,
        detail="high"
    )

    # Clean up temp file
    cleanup_temp_file(image_path)

    if result.success:
        # Send analysis
        await message.answer(
            f"✅ **{tool_name} - Анализ готов!**\n\n"
            f"📝 **Рекомендации:**\n{result.content}\n\n"
            f"💰 Использовано токенов: {result.tokens_used:,}"
        )

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка анализа изображения:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()

# ======================
# KLING MOTION CONTROL - Photo handler (must be before catch-all)
# ======================

@router.message(MediaState.kling_mc_waiting_for_image, F.photo)
async def kling_mc_receive_image(message: Message, state: FSMContext, user: User):
    """Receive reference image for Motion Control."""
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    temp_path = get_temp_file_path(prefix="kling_mc_image", suffix=".jpg")
    await message.bot.download_file(file.file_path, temp_path)

    # Resize if needed
    resize_image_if_needed(str(temp_path), max_size_mb=10.0, max_dimension=4096)

    await state.update_data(kling_mc_image_path=str(temp_path))
    await state.set_state(MediaState.kling_mc_waiting_for_video)

    await message.answer(
        "✅ Фото персонажа получено!\n\n"
        "🎬 Теперь отправьте ссылку на видео с движениями (URL).\n\n"
        "Требования к видео:\n"
        "• Формат: MP4/MOV (до 100 МБ)\n"
        "• Длительность: 3-30 секунд\n"
        "• Персонаж должен быть полностью виден\n"
        "• Без резких переходов и движений камеры\n"
        "• Рекомендуются реальные действия"
    )


# ======================
# SMART INPUT HANDLING - No model selected
# ======================

@router.message(F.photo, ~F.state(None))
async def handle_photo_in_wrong_state(message: Message, state: FSMContext):
    """Handle photo sent in unsupported state - redirect to correct handler."""
    current_state = await state.get_state()

    # If in video/image prompt state, pass to existing handlers
    if current_state in [
        MediaState.waiting_for_video_prompt,
        MediaState.waiting_for_image_prompt,
    ]:
        return  # Let other handlers process it

    # Otherwise, clear state and treat as new photo
    await state.clear()
    await handle_photo_no_model(message, state)


@router.message(F.photo)
async def handle_photo_no_model(message: Message, state: FSMContext):
    """Handle photo sent without selecting a model first."""
    # Download and save photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    # Create temp path
    temp_path = get_temp_file_path(prefix="unsorted", suffix=".jpg")

    await message.bot.download_file(file.file_path, temp_path)

    # Save to state
    await state.update_data(saved_photo_path=str(temp_path))
    await state.set_state(MediaState.waiting_for_photo_action_choice)

    # Create inline keyboard for choosing action
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Создать видео", callback_data="photo_action:video"),
            InlineKeyboardButton(text="🖼 Создать изображение", callback_data="photo_action:image")
        ],
        [
            InlineKeyboardButton(text="👁 Анализ фото", callback_data="photo_action:vision"),
            InlineKeyboardButton(text="🎨 Обработка фото", callback_data="photo_action:tools")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="photo_action:cancel")
        ]
    ])

    await message.answer_photo(
        photo=photo.file_id,
        caption="📸 Фото получено!\n\n"
                "Что вы хотите сделать с этим фото?\n\n"
                "🎬 Создать видео - генерация видео на основе фото\n"
                "🖼 Создать изображение - трансформация фото в новое изображение\n"
                "👁 Анализ фото - детальное описание содержимого\n"
                "🎨 Обработка фото - удаление фона, улучшение и т.д.",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("photo_action:"))
async def handle_photo_action_choice(callback: CallbackQuery, state: FSMContext):
    """Handle user's choice of what to do with the photo."""
    veo_billing = get_video_model_billing("veo-3.1-fast")
    luma_billing = get_video_model_billing("luma")
    kling_billing = get_video_model_billing("kling-video")
    nano_billing = get_image_model_billing("nano-banana-image")
    dalle_billing = get_image_model_billing("dalle3")
    action = callback.data.split(":")[1]

    data = await state.get_data()
    saved_photo_path = data.get("saved_photo_path")

    if action == "cancel":
        # Clean up photo
        if saved_photo_path:
            cleanup_temp_file(saved_photo_path)
        await state.clear()
        try:
            await callback.message.edit_caption(
                caption="❌ Операция отменена."
            )
        except Exception:
            pass
        await callback.answer()
        return

    if action == "video":
        # Show video models
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🌊 Veo 3.1", callback_data="photo_video:veo"),
                InlineKeyboardButton(text="🌙 Luma", callback_data="photo_video:luma")
            ],
            [
                InlineKeyboardButton(text="✨ Kling AI", callback_data="photo_video:kling")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="photo_action:back")
            ]
        ])

        caption_text = (
            f"🎬 Выберите модель для генерации видео:\n\n"
            f"• Veo 3.1 - Google, HD качество ({format_token_amount(veo_billing.tokens_per_generation)} токенов)\n"
            f"• Luma - Dream Machine ({format_token_amount(luma_billing.tokens_per_generation)} токенов)\n"
            f"• Kling AI - Высокое качество ({format_token_amount(kling_billing.tokens_per_generation)} токенов)"
        )

        try:
            await callback.message.edit_caption(caption=caption_text, reply_markup=keyboard)
        except Exception:
            try:
                await callback.message.answer(caption_text, reply_markup=keyboard)
            except Exception:
                pass
        await callback.answer()

    elif action == "image":
        # Show image models
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🍌 Nano Banana", callback_data="photo_image:nano"),
                InlineKeyboardButton(text="🖼 DALL-E", callback_data="photo_image:dalle")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="photo_action:back")
            ]
        ])

        caption_text = (
            f"🖼 Выберите модель для генерации изображения:\n\n"
            f"• Nano Banana - Gemini 2.5 Flash, image-to-image ({format_token_amount(nano_billing.tokens_per_generation)} токенов)\n"
            f"• DALL-E - Image variation ({format_token_amount(dalle_billing.tokens_per_generation)} токенов)"
        )

        try:
            await callback.message.edit_caption(caption=caption_text, reply_markup=keyboard)
        except Exception:
            try:
                await callback.message.answer(caption_text, reply_markup=keyboard)
            except Exception:
                pass
        await callback.answer()

    elif action == "vision":
        # Move photo to vision state and start analysis
        if saved_photo_path:
            # Actually process vision directly
            from app.database.models.user import User
            async with async_session_maker() as session:
                from sqlalchemy import select
                result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
                user = result.scalar_one_or_none()

                if user:
                    # Default prompt for analysis
                    prompt = "Provide a detailed analysis of this image. Describe what you see, including objects, people, scenery, colors, composition, and any notable details."
                    await _process_vision_with_path(callback.message, state, user, saved_photo_path, prompt)
                else:
                    await callback.message.edit_caption("❌ Ошибка: пользователь не найден")
                    await state.clear()
        else:
            await callback.answer("❌ Фото не найдено. Попробуйте еще раз.", show_alert=True)
            await state.clear()

    elif action == "tools":
        # Show photo tools
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🚫 Удалить фон", callback_data="photo_tool:remove_bg")
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="photo_action:back")
            ]
        ])

        try:
            await callback.message.edit_caption(
                caption="🎨 Выберите инструмент обработки:\n\n"
                        "• Удалить фон - прозрачный фон (~1,000 токенов)",
                reply_markup=keyboard
            )
        except Exception:
            try:
                await callback.message.answer(
                    "🎨 Выберите инструмент обработки:\n\n"
                    "• Удалить фон - прозрачный фон (~1,000 токенов)",
                    reply_markup=keyboard
                )
            except Exception:
                pass
        await callback.answer()

    elif action == "back":
        # Go back to main choice - resend the photo with choices
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Создать видео", callback_data="photo_action:video"),
                InlineKeyboardButton(text="🖼 Создать изображение", callback_data="photo_action:image")
            ],
            [
                InlineKeyboardButton(text="👁 Анализ фото", callback_data="photo_action:vision"),
                InlineKeyboardButton(text="🎨 Обработка фото", callback_data="photo_action:tools")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="photo_action:cancel")
            ]
        ])

        caption_text = (
            "📸 Фото получено!\n\n"
            "Что вы хотите сделать с этим фото?\n\n"
            "🎬 Создать видео - генерация видео на основе фото\n"
            "🖼 Создать изображение - трансформация фото в новое изображение\n"
            "👁 Анализ фото - детальное описание содержимого\n"
            "🎨 Обработка фото - удаление фона, улучшение и т.д."
        )

        try:
            await callback.message.edit_caption(caption=caption_text, reply_markup=keyboard)
        except Exception:
            try:
                await callback.message.answer(caption_text, reply_markup=keyboard)
            except Exception:
                pass
        await callback.answer()


@router.callback_query(F.data.startswith("photo_video:"))
async def handle_photo_video_model_choice(callback: CallbackQuery, state: FSMContext):
    """Handle video model choice after photo upload."""
    model = callback.data.split(":")[1]

    data = await state.get_data()
    saved_photo_path = data.get("saved_photo_path")

    # Move photo to image_path for video generation
    await state.update_data(image_path=saved_photo_path, service=model)
    await state.set_state(MediaState.waiting_for_video_prompt)

    model_names = {
        "veo": "Veo 3.1",
        "luma": "Luma Dream Machine",
        "kling": "Kling AI"
    }

    caption_text = (
        f"✅ Фото сохранено!\n\n"
        f"🎬 {model_names.get(model, model)}\n\n"
        f"📝 Теперь отправьте описание видео, которое вы хотите создать на основе этого фото.\n\n"
        f"Примеры:\n"
        f"• \"Оживи это фото, добавь плавное движение\"\n"
        f"• \"Сделай так, чтобы волосы развевались на ветру\"\n"
        f"• \"Добавь падающие снежинки и плавное движение камеры\""
    )

    try:
        await callback.message.edit_caption(caption=caption_text)
    except Exception:
        try:
            await callback.message.answer(caption_text)
        except Exception:
            pass
    await callback.answer()


@router.callback_query(F.data.startswith("photo_image:"))
async def handle_photo_image_model_choice(callback: CallbackQuery, state: FSMContext):
    """Handle image model choice after photo upload."""
    model = callback.data.split(":")[1]

    data = await state.get_data()
    saved_photo_path = data.get("saved_photo_path")

    # Map service names
    service_map = {
        "nano": "nano_banana",
        "dalle": "dalle"
    }

    # Move photo to reference_image_path for image generation
    await state.update_data(reference_image_path=saved_photo_path, service=service_map.get(model, model))
    await state.set_state(MediaState.waiting_for_image_prompt)

    model_names = {
        "nano": "Nano Banana",
        "dalle": "DALL-E"
    }

    examples = {
        "nano": "• \"Сделай в стиле аниме\"\n• \"Преобразуй в акварельный рисунок\"\n• \"Сделай фон космическим\"",
        "dalle": "• Отправьте любой текст для создания вариации"
    }

    caption_text = (
        f"✅ Фото сохранено!\n\n"
        f"🖼 {model_names.get(model, model)}\n\n"
        f"📝 Теперь отправьте описание изображения, которое вы хотите создать на основе этого фото.\n\n"
        f"Примеры:\n{examples.get(model, '')}"
    )

    try:
        await callback.message.edit_caption(caption=caption_text)
    except Exception:
        try:
            await callback.message.answer(caption_text)
        except Exception:
            pass
    await callback.answer()


@router.callback_query(F.data.startswith("photo_tool:"))
async def handle_photo_tool_choice(callback: CallbackQuery, state: FSMContext):
    """Handle photo tool choice."""
    tool = callback.data.split(":")[1]

    data = await state.get_data()
    saved_photo_path = data.get("saved_photo_path")

    if tool == "remove_bg":
        # Trigger processing with saved photo
        if saved_photo_path and os.path.exists(saved_photo_path):
            from app.database.models.user import User
            async with async_session_maker() as session:
                from sqlalchemy import select
                result = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
                user = result.scalar_one_or_none()

                if user:
                    await _process_remove_bg_with_path(callback.message, state, user, saved_photo_path)
                else:
                    await callback.message.edit_caption("❌ Ошибка: пользователь не найден")
                    await state.clear()
        else:
            await callback.answer("❌ Фото не найдено", show_alert=True)
            await state.clear()

    await callback.answer()


async def _process_remove_bg_with_path(message: Message, state: FSMContext, user: User, image_path: str):
    """Process background removal with given path."""
    estimated_tokens = 1000

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для удаления фона!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    progress_msg = await message.answer("🚫 Удаляю фон...")

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    removebg_service = RemoveBgService()
    result = await removebg_service.process_image(
        image_path=image_path,
        progress_callback=update_progress,
        size="auto",
        type="auto"
    )

    # Clean up temp file
    cleanup_temp_file(image_path)

    if result.success:
        result_file = FSInputFile(result.image_path)

        try:
            await message.answer_photo(
                photo=result_file,
                caption=f"✅ Фон удалён!\n\nИспользовано токенов: {estimated_tokens:,}"
            )
        except Exception:
            await message.answer_document(
                document=result_file,
                caption=f"✅ Фон удалён!\n\nИзображение с прозрачным фоном (PNG).\n\nИспользовано токенов: {estimated_tokens:,}"
            )

        try:
            pass  # os.remove(result.image_path) - DISABLED: files managed by file_cache
        except Exception:
            pass

        await progress_msg.delete()
    else:
        await progress_msg.edit_text(f"❌ Ошибка удаления фона:\n{result.error}")

    await state.clear()


async def _process_vision_with_path(message: Message, state: FSMContext, user: User, image_path: str, prompt: str):
    """Process vision analysis with given path."""
    estimated_tokens = 1500

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            cleanup_temp_file(image_path)
            await state.clear()
            return

    progress_msg = await message.answer("👁 Анализирую изображение...")

    vision_service = VisionService()
    result = await vision_service.analyze_image(
        image_path=image_path,
        prompt=prompt,
        model="gpt-4o",
        max_tokens=1500,
        detail="high"
    )

    # Clean up temp file
    cleanup_temp_file(image_path)

    if result.success:
        await message.answer(
            f"✅ **Анализ изображения готов!**\n\n"
            f"{result.content}\n\n"
            f"💰 Использовано токенов: {result.tokens_used:,}"
        )
        await progress_msg.delete()
    else:
        await progress_msg.edit_text(f"❌ Ошибка анализа:\n{result.error}")

    await state.clear()


# ======================
# KLING MOTION CONTROL HANDLERS
# ======================

@router.callback_query(F.data == "bot.kling_motion_control")
async def start_kling_motion_control(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling Motion Control flow."""
    mc_billing = get_video_model_billing("kling-motion-control")
    total_tokens = await get_available_tokens(user.id)
    tokens_per_request = mc_billing.tokens_per_generation
    videos_available = int(total_tokens / tokens_per_request) if total_tokens > 0 else 0

    # Get settings from state
    data = await state.get_data()
    mode = data.get("kling_mc_mode", "std")
    orientation = data.get("kling_mc_orientation", "image")
    keep_sound = data.get("kling_mc_sound", "yes")

    mode_display = "Стандартный" if mode == "std" else "Профессиональный"
    orientation_display = "По изображению" if orientation == "image" else "По видео"
    sound_display = "Да" if keep_sound == "yes" else "Нет"

    text = (
        "🕺 Kling AI — Motion Control\n\n"
        "Перенесите движения из видео на персонажа с изображения.\n\n"
        "📸 Отправьте фото персонажа (референсное изображение).\n\n"
        "Требования к фото:\n"
        "• Персонаж должен быть полностью виден (тело и голова)\n"
        "• Поддерживаются реалистичные и стилизованные персонажи\n"
        "• Форматы: JPG, JPEG, PNG (до 10 МБ)\n\n"
        f"⚙️ Настройки:\n"
        f"• Режим: {mode_display}\n"
        f"• Ориентация персонажа: {orientation_display}\n"
        f"• Сохранить звук: {sound_display}\n\n"
        f"💰 Стоимость: {format_token_amount(tokens_per_request)} токенов\n"
        f"🔹 Токенов хватит на {videos_available} видео"
    )

    await state.set_state(MediaState.kling_mc_waiting_for_image)
    await state.update_data(
        service="kling_motion_control",
        kling_mc_mode=mode,
        kling_mc_orientation=orientation,
        kling_mc_sound=keep_sound,
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=kling_motion_control_keyboard(mode, orientation, keep_sound)
        )
    except Exception:
        await callback.message.answer(
            text,
            reply_markup=kling_motion_control_keyboard(mode, orientation, keep_sound)
        )
    await callback.answer()


@router.callback_query(F.data == "kling_mc.settings")
async def kling_mc_settings_menu(callback: CallbackQuery, state: FSMContext):
    """Show Motion Control settings menu."""
    text = "⚙️ Настройки Motion Control\n\nВыберите параметр для изменения:"

    try:
        await callback.message.edit_text(text, reply_markup=kling_mc_settings_keyboard())
    except Exception:
        await callback.message.answer(text, reply_markup=kling_mc_settings_keyboard())
    await callback.answer()


@router.callback_query(F.data == "kling_mc.settings.mode")
async def kling_mc_mode_settings(callback: CallbackQuery, state: FSMContext):
    """Show Motion Control mode selection."""
    data = await state.get_data()
    current_mode = data.get("kling_mc_mode", "std")

    text = (
        "🎯 Режим генерации\n\n"
        "• Стандартный (std) — быстрая генерация\n"
        "• Профессиональный (pro) — более высокое качество, дольше"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_mc_mode_keyboard(current_mode))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_mc_mode_keyboard(current_mode))
    await callback.answer()


@router.callback_query(F.data.startswith("kling_mc.set.mode:"))
async def kling_mc_set_mode(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Motion Control mode."""
    new_mode = callback.data.split(":")[1]
    await state.update_data(kling_mc_mode=new_mode)
    await callback.answer(f"Режим: {'Стандартный' if new_mode == 'std' else 'Профессиональный'}")
    await start_kling_motion_control(callback, state, user)


@router.callback_query(F.data == "kling_mc.settings.orientation")
async def kling_mc_orientation_settings(callback: CallbackQuery, state: FSMContext):
    """Show Motion Control orientation selection."""
    data = await state.get_data()
    current = data.get("kling_mc_orientation", "image")

    text = (
        "🧍 Ориентация персонажа\n\n"
        "• По изображению — ориентация как на фото (макс. 10 сек. видео)\n"
        "• По видео — ориентация как в референсном видео (макс. 30 сек. видео)"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_mc_orientation_keyboard(current))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_mc_orientation_keyboard(current))
    await callback.answer()


@router.callback_query(F.data.startswith("kling_mc.set.orientation:"))
async def kling_mc_set_orientation(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Motion Control orientation."""
    new_val = callback.data.split(":")[1]
    await state.update_data(kling_mc_orientation=new_val)
    await callback.answer(f"Ориентация: {'По изображению' if new_val == 'image' else 'По видео'}")
    await start_kling_motion_control(callback, state, user)


@router.callback_query(F.data == "kling_mc.settings.sound")
async def kling_mc_sound_settings(callback: CallbackQuery, state: FSMContext):
    """Show Motion Control sound selection."""
    data = await state.get_data()
    current = data.get("kling_mc_sound", "yes")

    text = (
        "🔊 Звук из видео\n\n"
        "• Сохранить звук — оригинальный звук из видео будет в результате\n"
        "• Без звука — результат без аудио"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_mc_sound_keyboard(current))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_mc_sound_keyboard(current))
    await callback.answer()


@router.callback_query(F.data.startswith("kling_mc.set.sound:"))
async def kling_mc_set_sound(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Motion Control sound setting."""
    new_val = callback.data.split(":")[1]
    await state.update_data(kling_mc_sound=new_val)
    await callback.answer(f"Звук: {'Сохранить' if new_val == 'yes' else 'Без звука'}")
    await start_kling_motion_control(callback, state, user)


@router.message(MediaState.kling_mc_waiting_for_video, F.text)
async def kling_mc_receive_video_url(message: Message, state: FSMContext, user: User):
    """Receive reference video URL for Motion Control."""
    # Ignore commands
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    video_url = message.text.strip()

    # Basic URL validation
    if not video_url.startswith("http"):
        await message.answer(
            "❌ Пожалуйста, отправьте корректную ссылку на видео (URL).\n"
            "Ссылка должна начинаться с http:// или https://"
        )
        return

    await state.update_data(kling_mc_video_url=video_url)
    await state.set_state(MediaState.kling_mc_waiting_for_prompt)

    await message.answer(
        "✅ Ссылка на видео получена!\n\n"
        "📝 Отправьте текстовый промпт (необязательно).\n"
        "Промпт поможет добавить элементы и эффекты движения.\n\n"
        "Или отправьте /skip чтобы пропустить промпт и начать генерацию."
    )


@router.message(MediaState.kling_mc_waiting_for_prompt, F.text)
async def kling_mc_receive_prompt(message: Message, state: FSMContext, user: User):
    """Receive optional prompt and start Motion Control generation."""
    prompt = None
    if message.text and not message.text.startswith('/'):
        prompt = message.text.strip()
    # /skip or any command means no prompt

    data = await state.get_data()
    image_path = data.get("kling_mc_image_path")
    video_url = data.get("kling_mc_video_url")
    mode = data.get("kling_mc_mode", "std")
    orientation = data.get("kling_mc_orientation", "image")
    keep_sound = data.get("kling_mc_sound", "yes")

    if not image_path or not video_url:
        await message.answer("❌ Ошибка: изображение или видео не найдены. Попробуйте сначала.")
        await state.clear()
        return

    # Check and use tokens
    mc_billing = get_video_model_billing("kling-motion-control")
    estimated_tokens = mc_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            cleanup_temp_file(image_path)
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    progress_msg = await message.answer("🎬 Генерирую Motion Control видео с Kling AI...")

    await state.clear()

    # Generate video
    kling_service = KlingService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    result = await kling_service.generate_motion_control(
        image_path=image_path,
        video_url=video_url,
        mode=mode,
        character_orientation=orientation,
        prompt=prompt,
        keep_original_sound=keep_sound,
        progress_callback=update_progress,
    )

    # Cleanup temp image
    cleanup_temp_file(image_path)

    if result.success:
        from aiogram.types import FSInputFile

        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        caption_text = format_generation_message(
            content_type="видео (Motion Control)",
            model_name="Kling AI Motion Control",
            tokens_used=estimated_tokens,
            user_tokens=user_tokens,
            prompt=prompt
        )

        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=caption_text
        )
        await progress_msg.delete()

    else:
        # Refund tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.add_eternal_tokens(user.id, estimated_tokens, "refund")

        await progress_msg.edit_text(
            f"❌ Ошибка Motion Control:\n\n{result.error}\n\n"
            f"💰 Токены возвращены на баланс."
        )


@router.message(MediaState.kling_mc_waiting_for_video, F.video)
async def kling_mc_receive_video_file(message: Message, state: FSMContext, user: User):
    """Handle video file upload for Motion Control - inform user to send URL instead."""
    await message.answer(
        "⚠️ Пожалуйста, отправьте ссылку (URL) на видео, а не сам файл.\n\n"
        "Motion Control API принимает только URL видео.\n"
        "Загрузите видео на любой хостинг и отправьте ссылку."
    )


# ======================
# SEEDREAM HANDLERS
# ======================

@router.callback_query(F.data == "bot.seedream_4.5")
async def start_seedream_45(callback: CallbackQuery, state: FSMContext, user: User):
    """Seedream 4.5 image generation."""
    try:
        await cleanup_temp_images(state)
        await _show_seedream_menu(callback, state, user)
    except Exception as e:
        logger.error("seedream_start_error", error=str(e))
        try:
            await callback.message.answer(
                "❌ Ошибка при открытии Seedream. Попробуйте еще раз через меню."
            )
        except Exception:
            pass
        await callback.answer()


async def _show_seedream_menu(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Seedream 4.5 menu with current settings."""
    # Get current settings from state
    data = await state.get_data()
    current_size = data.get("seedream_size", "2K")
    batch_mode = data.get("seedream_batch_mode", False)
    batch_count = data.get("seedream_batch_count", 3)

    # Get billing info
    seedream_billing = get_image_model_billing("seedream-4.5")
    total_tokens = await get_available_tokens(user.id)
    tokens_per_image = seedream_billing.tokens_per_generation
    requests_available = int(total_tokens / tokens_per_image) if total_tokens > 0 else 0

    # Model info
    model_info = SeedreamService.get_model_info()

    text = (
        f"✨ **Seedream 4.5** — генерация изображений\n\n"
        f"📝 **Описание:** {model_info['description']}\n\n"
        f"🎯 **Возможности:**\n"
    )

    for cap in model_info['capabilities']:
        text += f"• {cap}\n"

    text += (
        f"\n⚙️ **Текущие настройки:**\n"
        f"• Разрешение: {current_size}\n"
        f"• Пакетная генерация: {'ВКЛ (' + str(batch_count) + ' шт.)' if batch_mode else 'ВЫКЛ'}\n\n"
        f"💰 **Стоимость:** {format_token_amount(tokens_per_image)} токенов за изображение\n"
        f"🔹 Токенов хватит на **{requests_available}** изображений\n\n"
        f"📸 **Отправьте:**\n"
        f"• Текстовое описание — для генерации по тексту\n"
        f"• Фото + описание — для генерации по фото"
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(
        service="seedream",
        seedream_version="4.5",
        seedream_size=current_size,
        seedream_batch_mode=batch_mode,
        seedream_batch_count=batch_count,
        reference_image_path=None,
        photo_caption_prompt=None
    )

    # Check if message has photo (can't edit_text on photo messages)
    try:
        if callback.message.photo:
            # Message is a photo - send new message instead of editing
            await callback.message.answer(
                text,
                reply_markup=seedream_keyboard(current_size, batch_mode),
                parse_mode="Markdown"
            )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=seedream_keyboard(current_size, batch_mode),
                parse_mode="Markdown"
            )
    except Exception:
        # Fallback: send new message if edit fails
        await callback.message.answer(
            text,
            reply_markup=seedream_keyboard(current_size, batch_mode),
            parse_mode="Markdown"
        )
    await callback.answer()


@router.callback_query(F.data == "seedream.settings.size")
async def seedream_size_settings(callback: CallbackQuery, state: FSMContext):
    """Show Seedream size selection."""
    data = await state.get_data()
    current_size = data.get("seedream_size", "2K")

    text = (
        f"📐 **Выберите разрешение изображения**\n\n"
        f"• **2K/4K** — автоматический размер по описанию\n"
        f"• **1:1, 16:9, 9:16...** — конкретное соотношение сторон\n\n"
        f"Текущий выбор: **{current_size}**"
    )

    await callback.message.edit_text(
        text,
        reply_markup=seedream_size_keyboard(current_size),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("seedream.set.size|"))
async def seedream_set_size(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Seedream size."""
    parts = callback.data.split("|")
    new_size = parts[1]

    await state.update_data(seedream_size=new_size)
    await callback.answer(f"Разрешение установлено: {new_size}")

    await _show_seedream_menu(callback, state, user)


@router.callback_query(F.data.startswith("seedream.toggle.batch|"))
async def seedream_toggle_batch(callback: CallbackQuery, state: FSMContext, user: User):
    """Toggle Seedream batch mode."""
    parts = callback.data.split("|")
    action = parts[1]

    new_batch_mode = (action == "on")
    await state.update_data(seedream_batch_mode=new_batch_mode)

    if new_batch_mode:
        await callback.answer("Пакетная генерация включена")
    else:
        await callback.answer("Пакетная генерация выключена")

    await _show_seedream_menu(callback, state, user)


@router.callback_query(F.data == "seedream.settings.batch_count")
async def seedream_batch_count_settings(callback: CallbackQuery, state: FSMContext):
    """Show Seedream batch count selection."""
    data = await state.get_data()
    current_count = data.get("seedream_batch_count", 3)

    text = (
        f"🔢 **Количество изображений в пакете**\n\n"
        f"При пакетной генерации модель создаст серию связанных изображений на основе вашего запроса.\n\n"
        f"⚠️ Стоимость = количество × цена за 1 изображение\n\n"
        f"Текущий выбор: **{current_count} шт.**"
    )

    await callback.message.edit_text(
        text,
        reply_markup=seedream_batch_count_keyboard(current_count),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("seedream.set.batch_count|"))
async def seedream_set_batch_count(callback: CallbackQuery, state: FSMContext, user: User):
    """Set Seedream batch count."""
    parts = callback.data.split("|")
    new_count = int(parts[1])

    await state.update_data(seedream_batch_count=new_count)
    await callback.answer(f"Количество изображений: {new_count}")

    await _show_seedream_menu(callback, state, user)


async def process_seedream_image(message: Message, user: User, state: FSMContext):
    """Process Seedream 4.5 image generation."""
    data = await state.get_data()
    prompt = data.get("photo_caption_prompt") or message.text
    size = data.get("seedream_size", "2K")
    batch_mode = data.get("seedream_batch_mode", False)
    batch_count = data.get("seedream_batch_count", 3)
    reference_image_path = data.get("reference_image_path")

    # Get billing info
    seedream_billing = get_image_model_billing("seedream-4.5")

    # Calculate estimated tokens
    images_count = batch_count if batch_mode else 1
    estimated_tokens = seedream_billing.tokens_per_generation * images_count

    # Check and reserve tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            # Clean up reference image if exists
            if reference_image_path:
                cleanup_temp_file(reference_image_path)

            await message.answer(
                f"❌ Недостаточно токенов для генерации!\n\n"
                f"Требуется: {format_token_amount(estimated_tokens)} токенов\n"
                f"Доступно: {format_token_amount(e.details['available'])} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Progress message
    mode_text = "по фото" if reference_image_path else "по тексту"
    progress_msg = await message.answer(
        f"✨ Генерирую {'изображения' if batch_mode else 'изображение'} {mode_text} с Seedream 4.5..."
    )

    seedream_service = SeedreamService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate image(s)
    result = await seedream_service.generate_image(
        prompt=prompt,
        progress_callback=update_progress,
        size=size,
        reference_image=reference_image_path,
        batch_mode=batch_mode,
        max_images=batch_count if batch_mode else 1,
        watermark=False
    )

    # Clean up reference image
    if reference_image_path:
        cleanup_temp_file(reference_image_path)

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)
        images_count = result.metadata.get("images_count", 1)
        all_images = result.metadata.get("all_images", [{"path": result.image_path}])

        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_available_tokens(user.id)

        # Send all images
        for idx, img_info in enumerate(all_images):
            img_path = img_info.get("path")
            if not img_path:
                continue

            try:
                # Generate caption for this image
                if idx == len(all_images) - 1:
                    # Last image - show full info
                    info_text = format_generation_message(
                        content_type=CONTENT_TYPES["image"],
                        model_name="Seedream 4.5",
                        tokens_used=tokens_used,
                        user_tokens=user_tokens,
                        prompt=prompt
                    )
                    if images_count > 1:
                        info_text = f"📸 Изображение {idx + 1}/{images_count}\n\n" + info_text

                    # Create action keyboard
                    builder = create_action_keyboard(
                        action_text="✨ Создать новое изображение",
                        action_callback="bot.seedream_4.5",
                        file_path=img_path,
                        file_type="image"
                    )

                    photo = FSInputFile(img_path)
                    await message.answer_photo(
                        photo=photo,
                        caption=info_text,
                        reply_markup=builder.as_markup()
                    )
                else:
                    # Not the last image - simple caption
                    photo = FSInputFile(img_path)
                    await message.answer_photo(
                        photo=photo,
                        caption=f"📸 Изображение {idx + 1}/{images_count}"
                    )

            except Exception as send_error:
                logger.error("seedream_image_send_failed", error=str(send_error), idx=idx)
                try:
                    doc_file = FSInputFile(img_path)
                    await message.answer_document(
                        document=doc_file,
                        caption=f"📸 Изображение {idx + 1}/{images_count}"
                    )
                except Exception:
                    pass

        await progress_msg.delete()

    else:
        # Refund tokens on error
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.add_eternal_tokens(user.id, estimated_tokens, "refund")

        await progress_msg.edit_text(
            f"❌ Ошибка генерации Seedream 4.5:\n\n{result.error}\n\n"
            f"💰 Токены возвращены на баланс."
        )

    await state.clear()


# ======================
# MIDJOURNEY IMAGE HANDLER
# ======================

async def process_midjourney_image(message: Message, user: User, state: FSMContext):
    """Process Midjourney image generation."""
    data = await state.get_data()
    prompt = data.get("photo_caption_prompt") or message.text
    reference_image_path = data.get("reference_image_path", None)

    mj_billing = get_image_model_billing("midjourney")
    estimated_tokens = mj_billing.tokens_per_generation

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            if reference_image_path:
                cleanup_temp_file(reference_image_path)
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    progress_msg = await message.answer("🎨 Генерирую изображение с Midjourney...")
    mj_service = MidjourneyService()

    # Run generation in background to not block the bot
    asyncio.create_task(
        _midjourney_generation_task(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user.id,
            prompt=prompt,
            estimated_tokens=estimated_tokens,
            progress_msg_id=progress_msg.message_id,
            mj_service=mj_service,
        )
    )

    await state.clear()


async def _midjourney_generation_task(
    bot,
    chat_id: int,
    user_id: int,
    prompt: str,
    estimated_tokens: int,
    progress_msg_id: int,
    mj_service,
):
    """Background task for Midjourney image generation. Runs without blocking the bot."""
    try:
        async def update_progress(text: str):
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_msg_id,
                    text=text,
                    parse_mode=None,
                )
            except Exception:
                pass

        result = await mj_service.generate_image(
            prompt=prompt,
            task_type="mj_txt2img",
            progress_callback=update_progress,
            aspect_ratio="16:9",
        )

        if result.success and result.image_paths:
            async with async_session_maker() as session:
                sub_service = SubscriptionService(session)
                user_tokens = await sub_service.get_available_tokens(user_id)

            caption = format_generation_message(
                content_type=CONTENT_TYPES["image"],
                model_name="Midjourney",
                tokens_used=estimated_tokens,
                user_tokens=user_tokens,
                prompt=prompt,
            )

            builder = create_action_keyboard(
                action_text=MODEL_ACTIONS["midjourney"]["text"],
                action_callback=MODEL_ACTIONS["midjourney"]["callback"],
                file_path=result.image_paths[0],
                file_type="image",
            )

            image_file = FSInputFile(result.image_paths[0])
            await bot.send_photo(
                chat_id=chat_id,
                photo=image_file,
                caption=caption,
                reply_markup=builder.as_markup(),
            )
            try:
                await bot.delete_message(chat_id=chat_id, message_id=progress_msg_id)
            except TelegramBadRequest as e:
                # Ignore expected errors when message can't be deleted
                if "message can't be deleted" not in str(e) and "message to delete not found" not in str(e):
                    from app.core.logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning("media_delete_message_failed", error=str(e))
            except Exception as e:
                from app.core.logger import get_logger
                logger = get_logger(__name__)
                logger.warning("media_delete_message_error", error=str(e))
        else:
            # Refund tokens
            async with async_session_maker() as session:
                sub_service = SubscriptionService(session)
                await sub_service.add_eternal_tokens(user_id, estimated_tokens, "refund")

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_msg_id,
                    text=f"❌ Ошибка генерации Midjourney:\n{result.error}\n\n"
                         f"💰 Токены возвращены на баланс.",
                    parse_mode=None,
                )
            except Exception:
                pass

    except Exception as e:
        logger.error("midjourney_background_task_failed", error=str(e), user_id=user_id)
        try:
            async with async_session_maker() as session:
                sub_service = SubscriptionService(session)
                await sub_service.add_eternal_tokens(user_id, estimated_tokens, "refund")
        except Exception:
            pass

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=progress_msg_id,
                text=f"❌ Ошибка генерации Midjourney:\n{str(e)[:200]}\n\n"
                     f"💰 Токены возвращены на баланс.",
                parse_mode=None,
            )
        except Exception:
            pass


# ======================
# MIDJOURNEY VIDEO HANDLER
# ======================

async def process_midjourney_video(message: Message, user: User, state: FSMContext):
    """Process Midjourney Video (image-to-video) generation using mj_video task type."""
    data = await state.get_data()
    prompt = data.get("photo_caption_prompt") or message.text or ""
    image_path = data.get("image_path", None)

    mj_billing = get_image_model_billing("midjourney")
    estimated_tokens = mj_billing.tokens_per_generation

    if not image_path:
        await message.answer(
            "⚠️ Midjourney Video требует фото.\n\n"
            "Отправьте фото с описанием движения в подписи."
        )
        return

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            cleanup_temp_file(image_path)
            await message.answer(
                f"❌ Недостаточно токенов!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов"
            )
            await state.clear()
            return

    progress_msg = await message.answer("🎬 Генерирую видео с Midjourney Video...")
    mj_service = MidjourneyService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Midjourney Video requires image URL - same limitation as Sora i2v
    cleanup_temp_file(image_path)
    await progress_msg.edit_text(
        "⚠️ **Midjourney Video временно недоступен**\n\n"
        "API требует загрузки изображения на CDN сервер.\n\n"
        "Используйте альтернативные сервисы для image-to-video:\n"
        "• 🌊 Veo 3.1\n"
        "• 🎥 Hailuo\n"
        "• 🎞 Kling",
        parse_mode="Markdown"
    )
    # Refund tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        await sub_service.add_eternal_tokens(user.id, estimated_tokens, "refund")

    await state.update_data(image_path=None, photo_caption_prompt=None)
