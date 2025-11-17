#!/usr/bin/env python3
# coding: utf-8

"""
Media handlers for video, audio, and image generation.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from pathlib import Path

from app.bot.keyboards.inline import back_to_main_keyboard
from app.database.models.user import User
from app.database.database import async_session_maker
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.services.video import VeoService
from app.services.image import DalleService, GeminiImageService, StabilityService, RemoveBgService
from app.services.subscription.subscription_service import SubscriptionService

logger = get_logger(__name__)

router = Router(name="media")


class MediaState(StatesGroup):
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()


# ======================
# VIDEO SERVICES
# ======================

@router.callback_query(F.data == "bot.veo")
async def start_veo(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "**Veo 3.1 - Video Generation**\n\n"
        "Google Veo создаёт реалистичные видео по вашему описанию.\n\n"
        "Длительность: 5-10 секунд\n"
        "Форматы: 16:9, 9:16, 1:1\n\n"
        "Стоимость: ~15,000 токенов за 5 секунд\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="veo")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.sora")
async def start_sora(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "**Sora 2 - Video Generation**\n\n"
        "Sora 2 может создавать реалистичные видео длительностью до 20 секунд по вашему описанию.\n\n"
        "Стоимость: ~15,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео, которое вы хотите создать."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="sora")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.luma")
async def start_luma(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Luma Dream Machine\n\n"
        "Luma создаёт качественные видео по вашему описанию.\n\n"
        "Стоимость: ~8,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="luma")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.hailuo")
async def start_hailuo(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Hailuo (MiniMax)\n\n"
        "Hailuo создаёт реалистичные видео.\n\n"
        "Стоимость: ~7,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="hailuo")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.kling")
async def start_kling(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Kling AI\n\n"
        "Kling создаёт высококачественные видео.\n\n"
        "Стоимость: ~9,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
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
    await state.update_data(service="kling_effects")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# IMAGE GENERATION
# ======================

@router.callback_query(F.data == "bot.gpt_image")
async def start_gpt_image(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "**GPT Image (DALL-E 3)**\n\n"
        "Создайте уникальные изображения по текстовому описанию.\n\n"
        "Модели:\n"
        "• DALL-E 3 (HD качество)\n"
        "• DALL-E 3 (стандарт)\n"
        "• DALL-E 2\n\n"
        "Размеры: 1024x1024, 1792x1024, 1024x1792\n\n"
        "Стоимость: 4,000-8,000 токенов\n\n"
        "Отправьте описание изображения."
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="dalle")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.nano")
async def start_nano(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "**Nano Banana (Gemini Imagen 3)**\n\n"
        "Google Imagen 3 для создания изображений.\n\n"
        "Форматы: 1:1, 16:9, 9:16, 3:4, 4:3\n\n"
        "Стоимость: ~3,000 токенов\n\n"
        "Отправьте описание изображения."
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="gemini_image")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# AUDIO SERVICES
# ======================

@router.callback_query(F.data == "bot.suno")
async def start_suno(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Suno AI – Music Generation\n\n"
        "Suno создаёт уникальную музыку и песни по вашему описанию.\n\n"
        "Стоимость: ~5,000 токенов за трек\n\n"
        "Отправьте описание музыки.\n\n"
        "Примеры:\n"
        "- Энергичная рок-композиция\n"
        "- Спокойная джазовая мелодия\n"
        "- Танцевальный электро-трек"
    )

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="suno")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.whisper_tts")
async def start_tts(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "OpenAI TTS – Text to Speech\n\n"
        "Превратите текст в естественную речь.\n\n"
        "Стоимость: ~200 токенов за запрос\n\n"
        "Доступные голоса:\n"
        "- alloy\n- echo\n- fable\n- onyx\n- nova\n- shimmer\n\n"
        "Отправьте текст для озвучки."
    )

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="tts")

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
    text = (
        "Замена фона\n\n"
        "Стоимость: ~500 токенов\n\n"
        "Отправьте изображение, затем укажите цвет фона (white, black, #FF5733)."
    )

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="replace_bg")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# FSM HANDLERS - VIDEO
# ======================

@router.message(MediaState.waiting_for_video_prompt, F.text)
async def process_video_prompt(message: Message, state: FSMContext, user: User):
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

    # Only Veo is implemented
    if service_name == "veo":
        await process_veo_video(message, user, state)
    else:
        await message.answer(
            f"Функция генерации видео ({display}) находится в разработке.\n"
            f"Ваш запрос получен: {message.text[:100]}..."
        )
        await state.clear()


async def process_veo_video(message: Message, user: User, state: FSMContext):
    """Process Veo video generation."""
    prompt = message.text

    # Check and use tokens
    estimated_tokens = 15000  # Veo is expensive

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)

        try:
            await sub_service.check_and_use_tokens(user.id, estimated_tokens)
        except InsufficientTokensError as e:
            await message.answer(
                f"❌ Недостаточно токенов для генерации видео!\n\n"
                f"Требуется: {estimated_tokens:,} токенов\n"
                f"Доступно: {e.details['available']:,} токенов\n\n"
                f"Купите подписку: /start → 💎 Подписка"
            )
            await state.clear()
            return

    # Send progress message
    progress_msg = await message.answer("🎬 Инициализация Veo 3.1...")

    # Create service
    veo_service = VeoService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text)
        except Exception:
            pass

    # Generate video
    result = await veo_service.generate_video(
        prompt=prompt,
        progress_callback=update_progress,
        duration=5,
        aspect_ratio="16:9"
    )

    if result.success:

        # Send video
        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=f"✅ Видео готово!\n\n"
                    f"Промпт: {prompt[:200]}\n"
                    f"Использовано токенов: {result.tokens_used:,}"
        )

        # Clean up
        try:
            os.remove(result.video_path)
        except Exception as e:
            logger.error("video_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        await progress_msg.edit_text(
            f"❌ Ошибка генерации видео:\n{result.error}"
        )

    await state.clear()


# ======================
# FSM HANDLERS - IMAGE GENERATION
# ======================

@router.message(MediaState.waiting_for_image_prompt, F.text)
async def process_image_prompt(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    service_name = data.get("service", "dalle")

    if service_name == "dalle":
        await process_dalle_image(message, user, state)
    elif service_name == "gemini_image":
        await process_gemini_image(message, user, state)
    else:
        await message.answer(
            f"Функция генерации изображений находится в разработке.\n"
            f"Ваш запрос получен: {message.text[:100]}..."
        )
        await state.clear()


async def process_dalle_image(message: Message, user: User, state: FSMContext):
    """Process DALL-E image generation."""
    prompt = message.text

    # Check and use tokens
    estimated_tokens = 4000  # DALL-E 3 standard

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
    dalle_service = DalleService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text)
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
            os.remove(result.image_path)
        except Exception as e:
            logger.error("image_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        await progress_msg.edit_text(
            f"❌ Ошибка генерации изображения:\n{result.error}"
        )

    await state.clear()


async def process_gemini_image(message: Message, user: User, state: FSMContext):
    """Process Gemini/Imagen image generation."""
    prompt = message.text

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
            await progress_msg.edit_text(text)
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
            os.remove(result.image_path)
        except Exception as e:
            logger.error("image_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        await progress_msg.edit_text(
            f"❌ Ошибка генерации изображения:\n{result.error}"
        )

    await state.clear()


# ======================
# FSM HANDLERS - AUDIO
# ======================

@router.message(MediaState.waiting_for_audio_prompt, F.text)
async def process_audio_prompt(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    service_name = data.get("service", "suno")

    display = {
        "suno": "Suno AI",
        "tts": "OpenAI TTS"
    }.get(service_name, service_name)

    await message.answer(
        f"Функция генерации аудио ({display}) находится в разработке.\n"
        f"Ваш текст получен: {message.text[:100]}..."
    )
    await state.clear()


# ======================
# FSM HANDLERS - IMAGE PROCESSING
# ======================

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
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{photo.file_id}.jpg"

    await message.bot.download_file(file.file_path, temp_path)

    # Create service
    stability_service = StabilityService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text)
        except Exception:
            pass

    # Upscale image
    result = await stability_service.upscale_image(
        image_path=str(temp_path),
        scale_factor=2,
        progress_callback=update_progress
    )

    # Clean up temp file
    try:
        os.remove(temp_path)
    except Exception:
        pass

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
            os.remove(result.image_path)
        except Exception as e:
            logger.error("upscale_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        await progress_msg.edit_text(
            f"❌ Ошибка улучшения изображения:\n{result.error}"
        )

    await state.clear()
