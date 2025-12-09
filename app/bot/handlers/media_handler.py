#!/usr/bin/env python3
# coding: utf-8

"""
Media handlers for video, audio, and image generation.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from pathlib import Path
from PIL import Image
import io

from app.bot.keyboards.inline import back_to_main_keyboard
from app.database.models.user import User
from app.database.database import async_session_maker
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.services.video import VeoService, SoraService, LumaService, HailuoService, KlingService
from app.services.image import DalleService, GeminiImageService, StabilityService, RemoveBgService, NanoBananaService
from app.services.audio import SunoService, OpenAIAudioService
from app.services.ai.vision_service import VisionService
from app.services.subscription.subscription_service import SubscriptionService

logger = get_logger(__name__)

router = Router(name="media")


class MediaState(StatesGroup):
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()
    waiting_for_whisper_audio = State()
    waiting_for_vision_image = State()
    waiting_for_vision_prompt = State()
    # Photo tools states
    waiting_for_photo_upscale = State()
    waiting_for_photo_replace_bg = State()
    waiting_for_photo_remove_bg = State()
    waiting_for_photo_vectorize = State()


# ======================
# VIDEO SERVICES
# ======================

@router.callback_query(F.data == "bot.veo")
async def start_veo(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "🌊 **Veo 3.1 - Video Generation**\n\n"
        "Google Veo создаёт реалистичные HD видео по вашему описанию.\n\n"
        "📊 **Параметры:**\n"
        "• Длительность: 8 секунд\n"
        "• Разрешение: 720p\n"
        "• Форматы: 16:9, 9:16, 1:1, 4:3, 3:4\n\n"
        "💰 **Стоимость:** ~15,000 токенов за видео\n\n"
        "✏️ **Отправьте описание видео**\n"
        "_Чем детальнее описание, тем лучше результат!_\n\n"
        "**Примеры:**\n"
        "• \"Золотой ретривер играет в поле подсолнухов\"\n"
        "• \"Чашка кофе на деревянном столе, утренний свет\"\n"
        "• \"Ночной город с потоками света машин\""
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
        "🍌 **Nano Banana (Gemini 2.5 Flash Image)**\n\n"
        "Gemini 2.5 Flash Image создаёт изображения по текстовому описанию.\n\n"
        "📊 **Параметры:**\n"
        "• Форматы: 1:1, 16:9, 9:16, 3:4, 4:3\n"
        "• Высокое качество изображений\n\n"
        "💰 **Стоимость:** ~3,000 токенов\n\n"
        "✏️ **Отправьте описание изображения**"
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="nano_banana")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
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
async def start_recraft(callback: CallbackQuery):
    """Recraft stub - under development."""
    text = (
        "🎨 **Recraft**\n\n"
        "⚠️ **Функционал в разработке**\n\n"
        "Интеграция с Recraft находится в процессе разработки.\n"
        "Пожалуйста, используйте альтернативные сервисы:\n\n"
        "• 🍌 Nano Banana (Gemini 2.5 Flash)\n"
        "• 🖼 DALL·E 3\n\n"
        "Следите за обновлениями!"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer("⚠️ Функционал в разработке", show_alert=False)


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
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate video
    result = await veo_service.generate_video(
        prompt=prompt,
        progress_callback=update_progress,
        duration=8,
        aspect_ratio="16:9",
        resolution="720p"
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
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации видео:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


async def process_sora_video(message: Message, user: User, state: FSMContext):
    """Process Sora 2 video generation."""
    prompt = message.text
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

    progress_msg = await message.answer("🎬 Инициализация Sora 2...")
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
        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=f"✅ Видео готово!\n\nПромпт: {prompt[:200]}\nТокенов: {result.tokens_used:,}"
        )
        try:
            os.remove(result.video_path)
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
    prompt = message.text
    estimated_tokens = 8000

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

    progress_msg = await message.answer("🎬 Инициализация Luma Dream Machine...")
    luma_service = LumaService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    result = await luma_service.generate_video(
        prompt=prompt,
        progress_callback=update_progress
    )

    if result.success:
        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=f"✅ Видео готово!\n\nПромпт: {prompt[:200]}\nТокенов: {result.tokens_used:,}"
        )
        try:
            os.remove(result.video_path)
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


async def process_hailuo_video(message: Message, user: User, state: FSMContext):
    """Process Hailuo (MiniMax) video generation."""
    prompt = message.text
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
        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=f"✅ Видео готово!\n\nПромпт: {prompt[:200]}\nТокенов: {result.tokens_used:,}"
        )
        try:
            os.remove(result.video_path)
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
    prompt = message.text
    estimated_tokens = 10000 if is_effects else 9000

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

    service_name = "Kling Effects" if is_effects else "Kling AI"
    progress_msg = await message.answer(f"🎬 Инициализация {service_name}...")
    kling_service = KlingService()

    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    result = await kling_service.generate_video(
        prompt=prompt,
        model="kling-v1.6-pro",
        progress_callback=update_progress
    )

    if result.success:
        video_file = FSInputFile(result.video_path)
        await message.answer_video(
            video=video_file,
            caption=f"✅ Видео готово!\n\nПромпт: {prompt[:200]}\nТокенов: {result.tokens_used:,}"
        )
        try:
            os.remove(result.video_path)
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
    elif service_name == "nano_banana":
        await process_nano_image(message, user, state)
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
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}"
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

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
            os.remove(result.image_path)
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
    """Process Nano Banana (Gemini 2.5 Flash Image) image generation."""
    prompt = message.text

    # Check and use tokens
    estimated_tokens = 3000  # Nano Banana cost

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
    progress_msg = await message.answer("🍌 Генерирую изображение с Nano Banana...")

    # Create service
    nano_service = NanoBananaService()

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    # Generate image
    result = await nano_service.generate_image(
        prompt=prompt,
        progress_callback=update_progress,
        aspect_ratio="1:1"
    )

    if result.success:
        tokens_used = result.metadata.get("tokens_used", estimated_tokens)

        # Optimize and send image
        try:
            # Check file size
            file_size = os.path.getsize(result.image_path)
            logger.info("nano_image_file_size", path=result.image_path, size=file_size)

            # If file is too large (>2MB) or to ensure compatibility, optimize it
            if file_size > 2 * 1024 * 1024:  # 2MB
                logger.info("nano_image_optimizing", original_size=file_size)

                # Open image with PIL
                img = Image.open(result.image_path)

                # Convert RGBA to RGB if needed (for JPEG)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background

                # Save as JPEG with quality reduction
                buffer = io.BytesIO()
                quality = 85
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                buffer.seek(0)

                optimized_size = buffer.getbuffer().nbytes
                logger.info("nano_image_optimized", original_size=file_size, new_size=optimized_size, quality=quality)

                # Send optimized image
                photo = BufferedInputFile(buffer.read(), filename="image.jpg")
                await message.answer_photo(
                    photo=photo,
                    caption=f"✅ Изображение готово!\n\n"
                            f"Промпт: {prompt[:200]}\n"
                            f"Использовано токенов: {tokens_used:,}"
                )
            else:
                # Try sending original PNG first
                try:
                    image_file = FSInputFile(result.image_path)
                    await message.answer_photo(
                        photo=image_file,
                        caption=f"✅ Изображение готово!\n\n"
                                f"Промпт: {prompt[:200]}\n"
                                f"Использовано токенов: {tokens_used:,}"
                    )
                except Exception as send_error:
                    logger.warning("nano_image_send_as_photo_failed", error=str(send_error))

                    # If sending as photo fails, try optimizing and re-sending
                    img = Image.open(result.image_path)

                    # Convert to RGB if needed
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background

                    # Save as JPEG
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=90, optimize=True)
                    buffer.seek(0)

                    logger.info("nano_image_converted_to_jpeg", original_format="PNG")

                    photo = BufferedInputFile(buffer.read(), filename="image.jpg")
                    await message.answer_photo(
                        photo=photo,
                        caption=f"✅ Изображение готово!\n\n"
                                f"Промпт: {prompt[:200]}\n"
                                f"Использовано токенов: {tokens_used:,}"
                    )

        except Exception as send_error:
            logger.error("nano_image_send_failed", error=str(send_error))
            # Last resort: try sending as document
            try:
                doc_file = FSInputFile(result.image_path)
                await message.answer_document(
                    document=doc_file,
                    caption=f"✅ Изображение готово (отправлено как файл)!\n\n"
                            f"Промпт: {prompt[:200]}\n"
                            f"Использовано токенов: {tokens_used:,}"
                )
            except Exception as doc_error:
                logger.error("nano_image_send_as_document_failed", error=str(doc_error))
                await message.answer(
                    f"✅ Изображение создано, но произошла ошибка при отправке.\n"
                    f"Изображение сохранено на сервере.\n"
                    f"Использовано токенов: {tokens_used:,}"
                )

        # Clean up
        try:
            os.remove(result.image_path)
        except Exception as e:
            logger.error("nano_image_cleanup_failed", error=str(e))

        await progress_msg.delete()
    else:
        try:
            await progress_msg.edit_text(
                f"❌ Ошибка генерации изображения:\n{result.error}",
                parse_mode=None
            )
        except Exception:
            # Ignore errors when message is not modified
            pass

    await state.clear()


# ======================
# FSM HANDLERS - AUDIO
# ======================

@router.message(MediaState.waiting_for_audio_prompt, F.text)
async def process_audio_prompt(message: Message, state: FSMContext, user: User):
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
        # Send audio
        audio_file = FSInputFile(result.audio_path)
        await message.answer_audio(
            audio=audio_file,
            caption=f"✅ Музыка готова!\n\n"
                    f"Промпт: {prompt[:200]}\n"
                    f"Использовано токенов: {estimated_tokens:,}",
            title=f"Suno AI - {prompt[:50]}"
        )

        # Clean up
        try:
            os.remove(result.audio_path)
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
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{file.file_id}.{file_ext}"

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
    try:
        os.remove(temp_path)
    except Exception:
        pass

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
            os.remove(result.audio_path)
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
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{photo.file_id}.jpg"

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
            try:
                os.remove(image_path)
            except Exception:
                pass
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
    try:
        os.remove(image_path)
    except Exception as e:
        logger.error("vision_image_cleanup_failed", error=str(e))

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
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{photo.file_id}.jpg"

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
        enhanced_path = temp_dir / f"enhanced_{photo.file_id}.jpg"

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
        try:
            os.remove(temp_path)
        except Exception:
            pass

        # Send enhanced image
        enhanced_file = FSInputFile(enhanced_path)
        await message.answer_photo(
            photo=enhanced_file,
            caption=f"✅ Изображение улучшено!\n\n"
                    f"Применены улучшения: резкость, контраст, цвета, яркость.\n\n"
                    f"Использовано токенов: {estimated_tokens:,}"
        )

        # Clean up enhanced file
        try:
            os.remove(enhanced_path)
        except Exception as e:
            logger.error("enhanced_image_cleanup_failed", error=str(e))

        await progress_msg.delete()

    except Exception as e:
        # Clean up temp files on error
        try:
            os.remove(temp_path)
        except Exception:
            pass

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
    """Process background replacement with user-specified background."""
    data = await state.get_data()
    image_path = data.get("saved_image_path")

    if not image_path or not os.path.exists(image_path):
        await message.answer("❌ Ошибка: фото не найдено. Попробуйте снова.")
        await state.clear()
        return

    bg_description = message.text

    # Check and use tokens (RemoveBG ~1000 + DALL-E ~4000)
    estimated_tokens = 5000

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
            try:
                os.remove(image_path)
            except Exception:
                pass
            await state.clear()
            return

    progress_msg = await message.answer("🖼️ Обрабатываю изображение...")

    # Progress callback
    async def update_progress(text: str):
        try:
            await progress_msg.edit_text(text, parse_mode=None)
        except Exception:
            pass

    try:
        # Step 1: Remove background
        await update_progress("🖼️ Удаляю фон с изображения...")

        removebg_service = RemoveBgService()
        remove_result = await removebg_service.process_image(
            image_path=image_path,
            size="auto",
            type="auto"
        )

        if not remove_result.success:
            raise Exception(f"Background removal failed: {remove_result.error}")

        # Step 2: Generate new background with DALL-E
        await update_progress("🎨 Создаю новый фон...")

        background_prompt = f"A high-quality background image: {bg_description}. Professional photography, suitable as a background."

        dalle_service = DalleService()
        bg_result = await dalle_service.generate_image(
            prompt=background_prompt,
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            style="natural"
        )

        if not bg_result.success:
            # Clean up removed bg image
            try:
                os.remove(remove_result.image_path)
            except Exception:
                pass
            raise Exception(f"Background generation failed: {bg_result.error}")

        # Step 3: Composite subject onto new background
        await update_progress("🖌️ Объединяю изображения...")

        from PIL import Image

        # Open images
        subject_img = Image.open(remove_result.image_path)  # RGBA
        background_img = Image.open(bg_result.image_path)  # RGB

        # Resize background to match subject size
        background_img = background_img.resize(subject_img.size, Image.Resampling.LANCZOS)

        # Convert background to RGBA
        background_img = background_img.convert('RGBA')

        # Composite
        final_img = Image.alpha_composite(background_img, subject_img)

        # Convert to RGB for JPEG
        final_rgb = Image.new('RGB', final_img.size, (255, 255, 255))
        final_rgb.paste(final_img, mask=final_img.split()[3])  # Use alpha as mask

        # Save final image
        temp_dir = Path("./storage/temp")
        final_path = temp_dir / f"replaced_{os.path.basename(image_path)}"
        final_rgb.save(str(final_path), 'JPEG', quality=95, optimize=True)

        # Clean up intermediate files
        try:
            os.remove(image_path)
            os.remove(remove_result.image_path)
            os.remove(bg_result.image_path)
        except Exception as e:
            logger.error("temp_files_cleanup_failed", error=str(e))

        # Send final image
        final_file = FSInputFile(final_path)
        await message.answer_photo(
            photo=final_file,
            caption=f"✅ Фон заменён!\n\n"
                    f"Новый фон: {bg_description}\n\n"
                    f"Использовано токенов: {estimated_tokens:,}"
        )

        # Clean up final file
        try:
            os.remove(final_path)
        except Exception as e:
            logger.error("final_image_cleanup_failed", error=str(e))

        await progress_msg.delete()

    except Exception as e:
        # Clean up all temp files on error
        try:
            os.remove(image_path)
        except Exception:
            pass

        logger.error("photo_replace_bg_failed", error=str(e))

        try:
            await progress_msg.edit_text(
                f"❌ Ошибка замены фона:\n{str(e)}"
            )
        except Exception:
            pass

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
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{photo.file_id}.jpg"

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
    try:
        os.remove(temp_path)
    except Exception:
        pass

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
            os.remove(result.image_path)
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
            try:
                os.remove(image_path)
            except Exception:
                pass
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
    try:
        os.remove(image_path)
    except Exception as e:
        logger.error("photo_tool_cleanup_failed", error=str(e))

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
