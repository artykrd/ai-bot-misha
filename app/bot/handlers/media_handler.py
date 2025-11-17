#!/usr/bin/env python3
# coding: utf-8
"""
Media handlers for video, audio, and image generation.
Includes FSM state handlers for processing user messages.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.keyboards.inline import back_to_main_keyboard
from app.database.models.user import User
from app.services.video.sora_service import SoraService
from app.services.video.luma_service import LumaService
from app.services.video.replicate_service import ReplicateService
from app.services.audio.suno_service import SunoService
from app.services.audio.openai_audio_service import OpenAIAudioService
from app.services.image.removebg_service import RemoveBgService
from app.services.image.stability_service import StabilityService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="media")


class MediaState(StatesGroup):
    """States for media generation."""
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()


# ===== VIDEO GENERATION BUTTONS =====

@router.callback_query(F.data == "bot.sora")
async def start_sora(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Sora video generation."""
    text = """☁️ **Sora 2 – Video Generation**

🎬 Sora 2 может создавать реалистичные видео длительностью до 20 секунд по вашему описанию.

**Стоимость:** ~15,000 токенов за видео

📝 Отправьте текстовое описание видео, которое вы хотите создать."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="sora")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.luma")
async def start_luma(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Luma video generation."""
    text = """📹 **Luma Dream Machine**

🎬 Luma создаёт качественные видео по вашему описанию.

**Стоимость:** ~8,000 токенов за видео

📝 Отправьте текстовое описание видео."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="luma")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.hailuo")
async def start_hailuo(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Hailuo video generation."""
    text = """🎥 **Hailuo (MiniMax)**

🎬 Hailuo создаёт реалистичные видео.

**Стоимость:** ~7,000 токенов за видео

📝 Отправьте текстовое описание видео."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="hailuo")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.kling")
async def start_kling(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling video generation."""
    text = """🎞 **Kling AI**

🎬 Kling создаёт высококачественные видео.

**Стоимость:** ~9,000 токенов за видео

📝 Отправьте текстовое описание видео."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.kling_effects")
async def start_kling_effects(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling Effects video generation."""
    text = """🧙 **Kling Effects**

🎬 Создание видео с эффектами от Kling AI.

**Стоимость:** ~10,000 токенов за видео

📝 Отправьте текстовое описание видео с эффектом."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling_effects")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.in_(["bot.veo", "bot.mjvideo"]))
async def service_not_configured(callback: CallbackQuery):
    """Handler for services requiring additional configuration."""
    service_names = {
        "bot.veo": "Veo 3.1",
        "bot.mjvideo": "Midjourney Video"
    }
    service = service_names.get(callback.data, "Сервис")

    await callback.answer(
        f"⚠️ {service} требует дополнительной настройки.\n\n"
        "Обратитесь к администратору: @gigavidacha",
        show_alert=True
    )


# ===== AUDIO GENERATION BUTTONS =====

@router.callback_query(F.data == "bot.suno")
async def start_suno(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Suno music generation."""
    text = """🎧 **Suno AI – Music Generation**

🎵 Suno создаёт уникальную музыку и песни по вашему описанию.

**Стоимость:** ~5,000 токенов за трек

📝 Отправьте описание музыки, которую хотите создать.

**Примеры:**
- "Энергичная рок-композиция с гитарой"
- "Спокойная джазовая мелодия для вечера"
- "Танцевальный электро трек"""

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="suno")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.whisper_tts")
async def start_tts(callback: CallbackQuery, state: FSMContext, user: User):
    """Start OpenAI TTS."""
    text = """🗣 **OpenAI TTS – Text to Speech**

🎙 Превратите текст в естественную речь.

**Стоимость:** ~200 токенов за запрос

**Доступные голоса:**
- alloy (нейтральный)
- echo (мужской)
- fable (выразительный)
- onyx (глубокий)
- nova (женский)
- shimmer (мягкий)

📝 Отправьте текст для озвучки."""

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="tts")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.whisper")
async def start_whisper(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Whisper transcription."""
    text = """🎙 **Whisper – Speech to Text**

🗣 Whisper расшифрует ваше голосовое сообщение в текст.

**Стоимость:** ~100 токенов за минуту

📱 Отправьте голосовое сообщение или аудиофайл."""

    await state.set_state(MediaState.waiting_for_image)  # Reusing state
    await state.update_data(service="whisper")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


# ===== IMAGE PROCESSING BUTTONS =====

@router.callback_query(F.data == "bot.pi_upscale")
async def start_upscale(callback: CallbackQuery, state: FSMContext, user: User):
    """Start image upscaling."""
    text = """🔎 **Улучшение качества фото**

✨ Увеличьте разрешение и улучшите качество вашего изображения.

**Стоимость:** ~2,000 токенов за изображение

📸 Отправьте изображение для улучшения."""

    await state.set_state(MediaState.waiting_for_upscale_image)
    await state.update_data(service="upscale")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.pi_remb")
async def start_remove_bg(callback: CallbackQuery, state: FSMContext, user: User):
    """Start background removal."""
    text = """🪞 **Удаление фона**

✂️ Удалите фон с вашего изображения.

**Стоимость:** ~500 токенов за изображение

📸 Отправьте изображение для удаления фона."""

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="remove_bg")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.pi_repb")
async def start_replace_bg(callback: CallbackQuery, state: FSMContext, user: User):
    """Start background replacement."""
    text = """🪄 **Замена фона**

🎨 Удалите старый фон и замените его на новый цвет.

**Стоимость:** ~500 токенов за изображение

📸 Отправьте изображение для замены фона.
После отправки укажите цвет (например: white, black, #FF5733)."""

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="replace_bg")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.in_(["bot.pi_vect", "bot.gpt_image", "bot.midjourney", "bot_stable_diffusion", "bot.recraft", "bot.faceswap"]))
async def image_generation_not_implemented(callback: CallbackQuery):
    """Placeholder for image generation services."""
    service_names = {
        "bot.pi_vect": "Векторизация",
        "bot.gpt_image": "GPT Image",
        "bot.midjourney": "Midjourney",
        "bot_stable_diffusion": "Stable Diffusion",
        "bot.recraft": "Recraft",
        "bot.faceswap": "FaceSwap"
    }
    service = service_names.get(callback.data, "Сервис")

    await callback.answer(
        f"⚠️ {service} будет доступен в следующей версии",
        show_alert=True
    )


# ===== MESSAGE HANDLERS FOR FSM STATES =====

@router.message(MediaState.waiting_for_video_prompt, F.text)
async def process_video_prompt(message: Message, state: FSMContext, user: User):
    """Process video generation prompt."""
    data = await state.get_data()
    service_name = data.get("service", "sora")
    prompt = message.text

    # Create progress callback
    async def progress_callback(status: str):
        try:
            await message.answer(status)
        except Exception as e:
            logger.error("progress_callback_failed", error=str(e))

    # Send initial message
    status_msg = await message.answer("⏳ Начинаю генерацию видео...")

    try:
        # Select appropriate service
        if service_name == "sora":
            service = SoraService()
            result = await service.generate_video(prompt, progress_callback=progress_callback)
        elif service_name == "luma":
            service = LumaService()
            result = await service.generate_video(prompt, progress_callback=progress_callback)
        elif service_name in ["hailuo", "kling", "kling_effects"]:
            service = ReplicateService()
            result = await service.generate_video(prompt, model=service_name, progress_callback=progress_callback)
        else:
            await message.answer("❌ Неизвестный сервис")
            await state.clear()
            return

        # Send result
        if result.success and result.video_path:
            video = FSInputFile(result.video_path)
            await message.answer_video(
                video,
                caption=f"✅ Видео создано!\n⏱ Время: {result.processing_time:.1f}с"
            )
        else:
            await message.answer(f"❌ Ошибка: {result.error}")

    except Exception as e:
        logger.error("video_generation_error", error=str(e), service=service_name)
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

    finally:
        await state.clear()


@router.message(MediaState.waiting_for_audio_prompt, F.text)
async def process_audio_prompt(message: Message, state: FSMContext, user: User):
    """Process audio generation prompt."""
    data = await state.get_data()
    service_name = data.get("service", "suno")
    prompt = message.text

    # Create progress callback
    async def progress_callback(status: str):
        try:
            await message.answer(status)
        except Exception as e:
            logger.error("progress_callback_failed", error=str(e))

    # Send initial message
    status_msg = await message.answer("⏳ Начинаю генерацию аудио...")

    try:
        if service_name == "suno":
            service = SunoService()
            result = await service.generate_audio(prompt, progress_callback=progress_callback)

            if result.success and result.audio_path:
                audio = FSInputFile(result.audio_path)
                await message.answer_audio(
                    audio,
                    caption=f"✅ Музыка создана!\n⏱ Время: {result.processing_time:.1f}с"
                )
            else:
                await message.answer(f"❌ Ошибка: {result.error}")

        elif service_name == "tts":
            service = OpenAIAudioService()
            voice = "alloy"  # Default voice
            result = await service.generate_audio(prompt, voice=voice, progress_callback=progress_callback)

            if result.success and result.audio_path:
                audio = FSInputFile(result.audio_path)
                await message.answer_audio(
                    audio,
                    caption=f"✅ Речь создана!\n⏱ Время: {result.processing_time:.1f}с"
                )
            else:
                await message.answer(f"❌ Ошибка: {result.error}")
        else:
            await message.answer("❌ Неизвестный сервис")

    except Exception as e:
        logger.error("audio_generation_error", error=str(e), service=service_name)
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

    finally:
        await state.clear()


@router.message(MediaState.waiting_for_image, F.photo)
async def process_image(message: Message, state: FSMContext, user: User):
    """Process image for background removal/replacement."""
    data = await state.get_data()
    service_name = data.get("service", "remove_bg")

    # Download image
    photo = message.photo[-1]  # Get largest photo
    file = await message.bot.get_file(photo.file_id)

    # Save to temp location
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        await message.bot.download_file(file.file_path, tmp)
        temp_path = tmp.name

    # Create progress callback
    async def progress_callback(status: str):
        try:
            await message.answer(status)
        except Exception as e:
            logger.error("progress_callback_failed", error=str(e))

    # Send initial message
    status_msg = await message.answer("⏳ Обрабатываю изображение...")

    try:
        service = RemoveBgService()

        if service_name == "remove_bg":
            result = await service.process_image(temp_path, progress_callback=progress_callback)
        elif service_name == "replace_bg":
            result = await service.replace_background(temp_path, background_color="white", progress_callback=progress_callback)
        else:
            await message.answer("❌ Неизвестный сервис")
            os.unlink(temp_path)
            await state.clear()
            return

        # Send result
        if result.success and result.image_path:
            photo_file = FSInputFile(result.image_path)
            await message.answer_photo(
                photo_file,
                caption=f"✅ Изображение обработано!\n⏱ Время: {result.processing_time:.1f}с"
            )
        else:
            await message.answer(f"❌ Ошибка: {result.error}")

    except Exception as e:
        logger.error("image_processing_error", error=str(e), service=service_name)
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

    finally:
        # Cleanup
        try:
            os.unlink(temp_path)
        except:
            pass
        await state.clear()


@router.message(MediaState.waiting_for_upscale_image, F.photo)
async def process_upscale(message: Message, state: FSMContext, user: User):
    """Process image upscaling."""
    # Download image
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    # Save to temp location
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        await message.bot.download_file(file.file_path, tmp)
        temp_path = tmp.name

    # Create progress callback
    async def progress_callback(status: str):
        try:
            await message.answer(status)
        except Exception as e:
            logger.error("progress_callback_failed", error=str(e))

    # Send initial message
    status_msg = await message.answer("⏳ Улучшаю изображение...")

    try:
        service = StabilityService()
        result = await service.upscale_image(temp_path, scale_factor=2, progress_callback=progress_callback)

        if result.success and result.image_path:
            photo_file = FSInputFile(result.image_path)
            await message.answer_photo(
                photo_file,
                caption=f"✅ Изображение улучшено!\n⏱ Время: {result.processing_time:.1f}с"
            )
        else:
            await message.answer(f"❌ Ошибка: {result.error}")

    except Exception as e:
        logger.error("upscale_error", error=str(e))
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

    finally:
        # Cleanup
        try:
            os.unlink(temp_path)
        except:
            pass
        await state.clear()
