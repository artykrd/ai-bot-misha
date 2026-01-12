#!/usr/bin/env python3
# coding: utf-8

"""
Media handlers for video, audio, and image generation.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
import os
from pathlib import Path
from PIL import Image
import io

from app.bot.keyboards.inline import (
    back_to_main_keyboard,
    kling_choice_keyboard,
    nano_banana_keyboard,
    nano_format_keyboard,
    nano_multi_images_keyboard
)
from app.bot.states import MediaState
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
from app.core.temp_files import get_temp_file_path, cleanup_temp_file
from app.services.video import VeoService, SoraService, LumaService, HailuoService, KlingService
from app.services.image import DalleService, GeminiImageService, StabilityService, RemoveBgService, NanoBananaService, KlingImageService, RecraftService
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
    total_tokens = user.get_total_tokens()
    videos_available = int(total_tokens / 98000) if total_tokens > 0 else 0

    text = (
        "🌊 Veo 3.1 · лучший генератор видео\n\n"
        "✏️ Нейросеть создает качественные 8 секундные видео, может имитировать голоса, "
        "сопровождать видео звуковой дорожкой и учитывать ваши пожелания.\n\n"
        "📸 При желании можно прикрепить 1 фото с промптом и создать видео на его основе.\n\n"
        "📷 1️⃣:2️⃣ (начальный кадр / завершающий кадр). Прикрепите два фото в одном запросе "
        "и получите видео на их основе. При желании можете прикрепить описание.\n\n"
        "#️⃣ Изучите гайд для того, чтобы создавать качественные видео и получать предсказуемые результаты.\n\n"
        "⚙️ Параметры\n"
        "Модель: Veo 3.1 Fast\n"
        "Формат: 16:9\n"
        "Сид: 0\n\n"
        f"🔹 Баланса хватит на {videos_available} видео. Стоимость генерации видео: 98 000 токенов"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="veo", image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.sora")
async def start_sora(callback: CallbackQuery, state: FSMContext, user: User):
    total_tokens = user.get_total_tokens()
    videos_available = int(total_tokens / 43000) if total_tokens > 0 else 0

    text = (
        "☁️ Sora 2 · вирусные ролики с озвучкой\n\n"
        "✏️ Нейросеть создает видео длиной до 15 секунд, в котором может быть звук, "
        "возможна озвучка сцен и персонажей в кадре, смена локаций и т.д.\n\n"
        "📸 При желании можно прикрепить 1 фото с промптом и создать видео на его основе.\n\n"
        "⛔️ Sora не может озвучивать людей на фото и делать так, чтобы они участвовали в кадре. "
        "Отправляйте фото без людей в кадре.\n\n"
        "⚙️ Параметры\n"
        "Длительность: 10 сек.\n"
        "Качество: стандартное\n"
        "Формат: 16:9\n\n"
        f"🔹 Баланса хватит на {videos_available} видео. Стоимость генерации видео (10 секунд): 43 000 токенов\n\n"
        "⚠️ Функционал в разработке."
    )

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.luma")
async def start_luma(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "🌙 **Luma Dream Machine**\n\n"
        "Luma создаёт качественные видео по вашему описанию.\n\n"
        "💰 **Стоимость:** Стоимость генерации видео: 85 000 токенов\n\n"
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
    total_tokens = user.get_total_tokens()
    videos_available = int(total_tokens / 90000) if total_tokens > 0 else 0

    text = (
        "🎥 Hailuo · создание видео\n\n"
        "✏️ Отправьте мне описание того, что хотите видеть на вашем видео. "
        "Сформулируйте конкретный запрос, например:\n"
        "└ Она словно сошла с кисти Вермеера, ее жемчужная серьга поблескивает. "
        "Эти загадочные глаза выходят за пределы холста, губы изгибаются в тонкой, элегантной улыбке, обращенной ко мне.\n"
        "└ Синее плюшевое существо на экране помешивает суп в кастрюле, от которого идет пар, "
        "после чего тарелка супа превращается в лёд, а синее плюшевое существо удивляется этому.\n\n"
        "⚙️ Настройки:\n"
        "Версия: t2v-01\n"
        "Автоперевод: включен\n\n"
        "📝 Выбранная модель принимает только текстовый запрос, вы можете изменить модель на понравившуюся "
        "или прикрепить фото с текстом и я автоматически изменю модель на t2v-01-director.\n\n"
        f"🔹 Токенов хватит на {videos_available} запросов. 1 запрос = 90,000 токенов."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="hailuo", image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.kling_effects")
async def start_kling_effects(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Kling Effects\n\n"
        "Создание видео с эффектами от Kling AI.\n\n"
        "Стоимость: ~10,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео с эффектом."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    # Clear old data when starting fresh session
    await state.update_data(service="kling_effects", image_path=None, photo_caption_prompt=None)

    await callback.message.answer(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# Handler for when user clicks "Kling" from main menu - show choice
@router.callback_query(F.data == "bot.kling_main")
async def start_kling_choice(callback: CallbackQuery, state: FSMContext, user: User):
    """Show Kling AI choice menu (photo or video)."""
    text = (
        "🎞 **Kling AI**\n\n"
        "Выберите тип генерации:\n\n"
        "🌄 **Создать фото** - генерация изображений\n"
        "🎬 **Создать видео** - генерация видео\n\n"
        "Kling AI создаёт высококачественный контент с помощью передовых алгоритмов."
    )

    await state.clear()  # Clear any previous state
    await callback.message.answer(text, reply_markup=kling_choice_keyboard())
    await callback.answer()


# Handler for Kling Image generation
@router.callback_query(F.data == "bot.kling_image")
async def start_kling_image(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling image generation - currently under development."""
    text = (
        "🎞 **Kling AI - Генерация изображений**\n\n"
        "⚠️ **Функционал в разработке**\n\n"
        "Интеграция с Kling Image находится в процессе разработки.\n"
        "Пожалуйста, используйте альтернативные сервисы:\n\n"
        "• 🍌 Nano Banana (Gemini 2.5 Flash)\n"
        "• 🍌✨ Banana PRO (Gemini 3 Pro)\n"
        "• 🖼 DALL·E 3\n\n"
        "Следите за обновлениями!"
    )

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer("⚠️ Функционал в разработке", show_alert=False)


# Handler for Kling Video generation (renamed from bot.kling)
@router.callback_query(F.data == "bot.kling_video")
async def start_kling_video(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling video generation."""
    total_tokens = user.get_total_tokens()
    videos_available = int(total_tokens / 80000) if total_tokens > 0 else 0

    text = (
        "🎞 Kling · меняй реальность\n\n"
        "✏️ Отправьте мне описание того, что хотите видеть на вашем видео, например:\n"
        "└ Оживи моё фото и сделай так, чтобы я улыбался и махал рукой в камеру. (прикрепите своё фото или фото близкого).\n"
        "└ Неоновое иайдзюцу: киберпанк-самурай в действии. (прикрепите своё фото).\n\n"
        "📷 Вы выбрали версию 2.5 Turbo: эта версия может принять до двух фото с промптом в одном запросе. "
        "Можно использовать как начальный кадр / конечный кадр.\n\n"
        "⚙️ Настройки:\n"
        "Длительность: 5 секунд\n"
        "Формат видео: 1:1\n"
        "Версия: 2.5\n"
        "Автоперевод: включен\n\n"
        f"🔹 Токенов хватит на {videos_available} запросов. 1 запрос = 80,000.0 токенов."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling", image_path=None, photo_caption_prompt=None)

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# IMAGE GENERATION
# ======================

@router.callback_query(F.data == "bot.gpt_image")
async def start_gpt_image(callback: CallbackQuery, state: FSMContext, user: User):
    # Clean up any old images
    await cleanup_temp_images(state)

    text = (
        "**GPT Image (DALL-E 3)**\n\n"
        "Создайте уникальные изображения по текстовому описанию.\n\n"
        "📊 **Модели:**\n"
        "• DALL-E 3 (HD качество)\n"
        "• DALL-E 3 (стандарт)\n"
        "• DALL-E 2\n\n"
        "**Размеры:** 1024x1024, 1792x1024, 1024x1792\n\n"
        "💰 **Стоимость генерации: 8 500 токенов за изображение**\n\n"
        "🎨 **Режимы работы:**\n"
        "• **Text-to-Image:** Отправьте описание изображения\n"
        "• **Image Variation (DALL-E 2):** Отправьте фото для создания вариаций\n\n"
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

    text = (
        "🍌 **Nano Banana (Gemini 2.5 Flash Image)**\n\n"
        "Gemini 2.5 Flash Image создаёт изображения по текстовому описанию.\n\n"
        "📊 **Параметры:**\n"
        "• Форматы: 1:1, 16:9, 9:16, 3:4, 4:3\n"
        "• Высокое качество изображений\n\n"
        "💰 **Стоимость:** ~3,000 токенов за изображение\n\n"
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

    text = (
        "🍌✨ **Banana PRO (Gemini 3 Pro Image)**\n\n"
        "Gemini 3 Pro Image - это новейшая модель с улучшенными возможностями генерации.\n\n"
        "📊 **Параметры:**\n"
        "• Форматы: 1:1, 16:9, 9:16, 4:3, 3:4 и другие\n"
        "• Размеры: 2K, 4K\n"
        "• Высочайшее качество изображений\n"
        "• Улучшенная генерация текста на изображениях\n\n"
        "💰 **Стоимость:** ~3,000 токенов за изображение\n\n"
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
async def start_midjourney(callback: CallbackQuery):
    """Midjourney stub - under development."""
    text = (
        "🌆 **Midjourney**\n\n"
        "⚠️ **Функционал в разработке**\n\n"
        "Интеграция с Midjourney находится в процессе разработки.\n"
        "Пожалуйста, используйте альтернативные сервисы:\n\n"
        "• 🍌 Nano Banana (Gemini 2.5 Flash)\n"
        "• 🖼 DALL·E 3\n\n"
        "Следите за обновлениями!"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer("⚠️ Функционал в разработке", show_alert=False)


@router.callback_query(F.data == "bot_stable_diffusion")
async def start_stable_diffusion(callback: CallbackQuery):
    """Stable Diffusion stub - under development."""
    text = (
        "🖌 **Stable Diffusion**\n\n"
        "⚠️ **Функционал в разработке**\n\n"
        "Интеграция с Stable Diffusion находится в процессе разработки.\n"
        "Пожалуйста, используйте альтернативные сервисы:\n\n"
        "• 🍌 Nano Banana (Gemini 2.5 Flash)\n"
        "• 🖼 DALL·E 3\n\n"
        "Следите за обновлениями!"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer("⚠️ Функционал в разработке", show_alert=False)


@router.callback_query(F.data == "bot.recraft")
async def start_recraft(callback: CallbackQuery, state: FSMContext, user: User):
    """Recraft AI image generation."""
    # Clean up any old images
    await cleanup_temp_images(state)

    text = (
        "🎨 **Recraft AI - Image Generation**\n\n"
        "Recraft создаёт высококачественные изображения в различных стилях.\n\n"
        "📊 **Параметры:**\n"
        "• Модель: Recraft V2 (оптимальное соотношение цена/качество)\n"
        "• Стили: реалистичные, иллюстрации, векторная графика, иконки\n"
        "• Размеры: 1024x1024 и другие соотношения\n\n"
        "💰 **Стоимость:** ~2,200 токенов (дешевле DALL-E 3)\n\n"
        "🎨 **Доступные стили:**\n"
        "• **Realistic Image** (по умолчанию) - фотореалистичные изображения\n"
        "• **Digital Illustration** - цифровые иллюстрации\n"
        "• **Vector Illustration** - векторная графика\n"
        "• **Icon** - иконки и символы\n\n"
        "✏️ **Отправьте описание изображения**\n\n"
        "**Примеры:**\n"
        "• \"Реалистичный портрет кота в космосе\"\n"
        "• \"Цифровая иллюстрация дракона в стиле фэнтези\"\n"
        "• \"Векторная иконка дома в минималистичном стиле\"\n"
        "• \"Закат на берегу океана с пальмами\""
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
    else:
        # No caption - ask for description
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
        "kling_effects": "Kling Effects"
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
    else:
        await message.answer(
            f"Функция генерации видео ({display}) находится в разработке.\n"
            f"Ваш запрос получен: {message.text[:100]}..."
        )
        await state.clear()


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
        f"Стоимость: ~{estimated_tokens:,} токенов (≈${cost_estimate.estimated_cost_usd:.2f})\n\n"
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
        f"💰 Стоимость: ~{estimated_tokens:,} токенов\n\n"
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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
    """Process Sora 2 video generation."""
    # Get state data
    data = await state.get_data()
    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    estimated_tokens = 15000

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

    progress_msg = await message.answer("🎬 Генерирую видео...")
    sora_service = SoraService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    result = await sora_service.generate_video(
        prompt=prompt,
        model="sora-2",
        progress_callback=update_progress
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_user_total_tokens(user.id)

        # Generate unified notification message
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name="Sora 2",
            tokens_used=result.tokens_used,
            user_tokens=user_tokens,
            prompt=prompt
        )

        # Create action keyboard
        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["sora"]["text"],
            action_callback=MODEL_ACTIONS["sora"]["callback"],
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


async def process_luma_video(message: Message, user: User, state: FSMContext):
    """Process Luma Dream Machine video generation."""
    # Get state data (check if image was provided)
    data = await state.get_data()

    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    image_path = data.get("image_path", None)

    estimated_tokens = 8000

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
    estimated_tokens = 7000

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
    """Process Kling AI video generation."""
    # Get state data (check if image was provided)
    data = await state.get_data()

    # Get prompt from caption if available, otherwise from message text
    prompt = data.get("photo_caption_prompt") or message.text
    image_path = data.get("image_path", None)

    estimated_tokens = 10000 if is_effects else 9000

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

    service_name = "Kling Effects" if is_effects else "Kling AI"
    mode_text = "image-to-video" if image_path else "text-to-video"
    progress_msg = await message.answer(f"🎬 Инициализация {service_name} ({mode_text})...")
    kling_service = KlingService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # For Kling, we would need to upload the image first or provide URL
    # For simplicity, we'll pass image_path and let service handle upload if needed
    kwargs = {}
    if image_path:
        # Note: Kling API expects image_url, so service needs to handle upload
        # For now, we'll pass the local path as image_url parameter
        kwargs["image_url"] = image_path

    result = await kling_service.generate_video(
        prompt=prompt,
        model="kling-v1.6-pro",
        progress_callback=update_progress,
        **kwargs
    )

    if result.success:
        # Get user's remaining tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_user_total_tokens(user.id)

        # Generate unified notification message
        mode_info = "image-to-video" if image_path else "text-to-video"
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name=service_name,  # "Kling AI" or "Kling Effects"
            tokens_used=result.tokens_used,
            user_tokens=user_tokens,
            prompt=prompt,
            mode=mode_info
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
            "dalle": "DALL-E"
        }.get(service_name, service_name)

        # Check if photo has caption (description) - if yes, process immediately
        if message.caption and message.caption.strip():
            await state.update_data(photo_caption_prompt=message.caption.strip())

            # Route to appropriate image service
            if service_name == "nano_banana":
                await process_nano_image(message, user, state)
            elif service_name == "dalle":
                await process_dalle_image(message, user, state)
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
            "dalle": "DALL-E"
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
    estimated_tokens = 2000 if reference_image_path else 4000  # Variations are cheaper

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
    estimated_tokens = 3000  # Imagen 3

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
    cost_per_image = 3000  # Nano Banana cost per image
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
                user_tokens = await sub_service.get_user_total_tokens(user.id)

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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

    prompt = data.get("photo_caption_prompt") or message.text
    reference_image_path = data.get("reference_image_path", None)

    estimated_tokens = 5000 if reference_image_path else 3000  # Kling image cost

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
    progress_msg = await message.answer(
        f"🎞 Генерирую изображение с Kling AI ({mode_text})..."
    )

    kling_service = KlingImageService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate image
    result = await kling_service.generate_image(
        prompt=prompt,
        model="kling-v1",  # Default model
        progress_callback=update_progress,
        aspect_ratio="1:1",  # Default aspect ratio
        resolution="1k"  # Default resolution
    )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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

    estimated_tokens = 2200  # Recraft V2 cost (cheaper than DALL-E 3)

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
            await progress_msg.edit_text(
                f"❌ Ошибка улучшения изображения:\n{str(e)}"
            )
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

    # Check and use tokens (Gemini image-to-image: ~3000 tokens)
    estimated_tokens = 3000

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
            user_tokens = await sub_service.get_user_total_tokens(user.id)

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
# SMART INPUT HANDLING - No model selected
# ======================

@router.message(F.photo, ~F.state(None))
async def handle_photo_in_wrong_state(message: Message, state: FSMContext):
    """Handle photo sent in unsupported state - redirect to correct handler."""
    current_state = await state.get_state()

    # If in video/image prompt state, pass to existing handlers
    if current_state in [MediaState.waiting_for_video_prompt, MediaState.waiting_for_image_prompt]:
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
        caption="📸 **Фото получено!**\n\n"
                "Что вы хотите сделать с этим фото?\n\n"
                "🎬 **Создать видео** - генерация видео на основе фото\n"
                "🖼 **Создать изображение** - трансформация фото в новое изображение\n"
                "👁 **Анализ фото** - детальное описание содержимого\n"
                "🎨 **Обработка фото** - удаление фона, улучшение и т.д.",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("photo_action:"))
async def handle_photo_action_choice(callback: CallbackQuery, state: FSMContext):
    """Handle user's choice of what to do with the photo."""
    action = callback.data.split(":")[1]

    data = await state.get_data()
    saved_photo_path = data.get("saved_photo_path")

    if action == "cancel":
        # Clean up photo
        if saved_photo_path:
            cleanup_temp_file(saved_photo_path)
        await state.clear()
        await callback.message.edit_caption(
            caption="❌ Операция отменена."
        )
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

        await callback.message.edit_caption(
            caption="🎬 **Выберите модель для генерации видео:**\n\n"
                    "• **Veo 3.1** - Google, HD качество (~15,000 токенов)\n"
                    "• **Luma** - Dream Machine (~8,000 токенов)\n"
                    "• **Kling AI** - Высокое качество (~9,000 токенов)",
            reply_markup=keyboard
        )
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

        await callback.message.edit_caption(
            caption="🖼 **Выберите модель для генерации изображения:**\n\n"
                    "• **Nano Banana** - Gemini 2.5 Flash, image-to-image (~3,000 токенов)\n"
                    "• **DALL-E** - Image variation (~2,000 токенов)",
            reply_markup=keyboard
        )
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

        await callback.message.edit_caption(
            caption="🎨 **Выберите инструмент обработки:**\n\n"
                    "• **Удалить фон** - прозрачный фон (~1,000 токенов)",
            reply_markup=keyboard
        )
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

        await callback.message.edit_caption(
            caption="📸 **Фото получено!**\n\n"
                    "Что вы хотите сделать с этим фото?\n\n"
                    "🎬 **Создать видео** - генерация видео на основе фото\n"
                    "🖼 **Создать изображение** - трансформация фото в новое изображение\n"
                    "👁 **Анализ фото** - детальное описание содержимого\n"
                    "🎨 **Обработка фото** - удаление фона, улучшение и т.д.",
            reply_markup=keyboard
        )
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

    await callback.message.edit_caption(
        caption=f"✅ Фото сохранено!\n\n"
                f"🎬 **{model_names.get(model, model)}**\n\n"
                f"📝 Теперь отправьте описание видео, которое вы хотите создать на основе этого фото.\n\n"
                f"**Примеры:**\n"
                f"• \"Оживи это фото, добавь плавное движение\"\n"
                f"• \"Сделай так, чтобы волосы развевались на ветру\"\n"
                f"• \"Добавь падающие снежинки и плавное движение камеры\""
    )
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

    await callback.message.edit_caption(
        caption=f"✅ Фото сохранено!\n\n"
                f"🖼 **{model_names.get(model, model)}**\n\n"
                f"📝 Теперь отправьте описание изображения, которое вы хотите создать на основе этого фото.\n\n"
                f"**Примеры:**\n{examples.get(model, '')}"
    )
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
