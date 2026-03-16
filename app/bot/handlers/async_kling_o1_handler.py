"""
Async Kling O1 video handler using job queue.

Kling O1 (Omni Video) supports:
- Text-to-video
- Image/element reference (images uploaded by user)
- Video editing (user uploads a video as base)

Uploaded media types:
- Photos → stored in image_list (referenced as @Image1, @Image2 etc.)
- Videos → stored as video_url (referenced as @Video1)

User writes prompt with @Image1, @Video1 references.
Bot translates them to API format (<<<image_1>>>, <<<video_1>>>).
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states.media import MediaState, KlingO1Settings, clear_state_preserve_settings
from app.database.models.user import User
from app.database.database import async_session_maker
from app.database.models.system import SystemSetting
from app.services.subscription.subscription_service import SubscriptionService
from app.services.video_job_service import VideoJobService
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.core.billing_config import get_kling_o1_tokens_cost
from sqlalchemy import select

logger = get_logger(__name__)

router = Router(name="async_kling_o1")

# Max images allowed
MAX_IMAGES_WITH_VIDEO = 4
MAX_IMAGES_WITHOUT_VIDEO = 7


async def is_async_enabled() -> bool:
    """Check if async video is enabled."""
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SystemSetting).where(SystemSetting.key == "async_video_enabled")
            )
            setting = result.scalar_one_or_none()
            if not setting:
                return True
            return setting.value.lower() in ("true", "1", "yes")
    except Exception:
        return True


def _get_video_telegram_url(bot_token: str, file_path: str) -> str:
    """Build Telegram file download URL from file_path."""
    return f"https://api.telegram.org/file/bot{bot_token}/{file_path}"


def _build_media_summary(images: list, video_url: str) -> str:
    """Build a summary string of uploaded media."""
    parts = []
    if video_url:
        parts.append("🎬 Видео: 1 файл (@Video1)")
    for i, _ in enumerate(images, 1):
        parts.append(f"🖼 Фото {i} (@Image{i})")
    return "\n".join(parts) if parts else "нет загруженных медиафайлов"


async def create_kling_o1_video_job(
    message: Message,
    user: User,
    state: FSMContext,
    prompt: str,
) -> bool:
    """
    Create async video generation job for Kling O1.

    Returns:
        True if job created successfully, False otherwise
    """
    data = await state.get_data()
    o1_settings = KlingO1Settings.from_dict(data)

    # Auto-translate if enabled
    if o1_settings.auto_translate and prompt:
        try:
            from app.services.ai.openai_service import OpenAIService
            openai_service = OpenAIService()
            translated = await openai_service.translate_to_english(prompt)
            if translated:
                prompt = translated
        except Exception as e:
            logger.warning("kling_o1_translate_failed", error=str(e))

    # Get media
    images = data.get("kling_o1_images", [])
    video_url = data.get("kling_o1_video_url", None)
    video_is_base = data.get("kling_o1_video_is_base", True)

    # Calculate tokens
    estimated_tokens = get_kling_o1_tokens_cost(o1_settings.mode, o1_settings.duration)
    model_id = f"kling_o1-{o1_settings.mode}"

    # Check and use tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(
                user.id,
                estimated_tokens,
                model_id=model_id
            )
        except InsufficientTokensError as e:
            from app.utils.file_utils import cleanup_temp_file
            for img_path in images:
                cleanup_temp_file(img_path)

            error_details = e.details
            if error_details.get("unlimited_limit_reached"):
                await message.answer(
                    f"❌ {e.message}\n\n"
                    "Лимит безлимитной подписки достигнут."
                )
            else:
                await message.answer(
                    f"❌ Недостаточно токенов!\n\n"
                    f"Требуется: {estimated_tokens:,} токенов\n"
                    f"Доступно: {error_details['available']:,} токенов"
                )

            await clear_state_preserve_settings(state)
            return False

    # Send queue message
    progress_msg = await message.answer(
        "⏳ Ваше видео Kling O1 добавлено в очередь на генерацию!\n\n"
        "Мы отправим вам результат, как только он будет готов. "
        "Это может занять от 5 до 15 минут.\n\n"
        "Вы можете продолжать пользоваться ботом, пока видео генерируется."
    )

    try:
        async with async_session_maker() as session:
            job_service = VideoJobService(session)

            input_data = {
                "images": images,
                "video_url": video_url,
                "video_is_base": video_is_base,
                "duration": o1_settings.duration,
                "aspect_ratio": o1_settings.aspect_ratio,
                "mode": o1_settings.mode,
                "keep_original_sound": "yes",
            }

            from app.services.logging import ai_logger
            ai_request_id = await ai_logger.log_operation(
                user_id=user.id,
                model_id=model_id,
                operation_category="video_gen",
                tokens_cost=estimated_tokens,
                prompt=prompt[:500],
                status="pending",
                input_data=input_data,
                units=1.0,
                request_type="video"
            )

            job = await job_service.create_job(
                user_id=user.id,
                provider="kling_o1",
                model_id="kling-video-o1",
                prompt=prompt,
                input_data=input_data,
                chat_id=message.chat.id,
                tokens_cost=estimated_tokens,
                progress_message_id=progress_msg.message_id,
                ai_request_id=ai_request_id
            )

            logger.info(
                "kling_o1_video_job_created",
                user_id=user.id,
                job_id=job.id,
                model=model_id,
                tokens=estimated_tokens,
                mode=o1_settings.mode,
                duration=o1_settings.duration,
                images_count=len(images),
                has_video=bool(video_url),
            )

    except Exception as e:
        logger.error("kling_o1_job_creation_failed", error=str(e), user_id=user.id)

        # Refund tokens via rollback (creates refund subscription to avoid wrong-sub bug)
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.rollback_tokens(user.id, estimated_tokens)

        await progress_msg.edit_text(
            f"❌ Ошибка создания задачи: {str(e)[:200]}\n\n"
            "Токены возвращены на ваш счёт."
        )
        return False

    finally:
        await clear_state_preserve_settings(state)

    return True


# ============================================================
# STATE: kling_o1_waiting_for_input
# ============================================================

@router.message(MediaState.kling_o1_waiting_for_input, F.text)
async def process_kling_o1_text(message: Message, state: FSMContext, user: User):
    """
    Process text message in Kling O1 input state.
    If media is already uploaded → ask user to press Continue or include prompt.
    If no media → treat as direct text-to-video prompt.
    """
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return

    data = await state.get_data()
    images = data.get("kling_o1_images", [])
    video_url = data.get("kling_o1_video_url", None)

    if images or video_url:
        # Media uploaded, but user sent text — use it as prompt
        if await is_async_enabled():
            await create_kling_o1_video_job(message, user, state, message.text.strip())
        else:
            await message.answer("❌ Асинхронная генерация временно отключена.")
            await clear_state_preserve_settings(state)
    else:
        # No media — text-to-video
        if await is_async_enabled():
            await create_kling_o1_video_job(message, user, state, message.text.strip())
        else:
            await message.answer("❌ Асинхронная генерация временно отключена.")
            await clear_state_preserve_settings(state)


@router.message(MediaState.kling_o1_waiting_for_input, F.photo)
async def process_kling_o1_photo(message: Message, state: FSMContext, user: User):
    """
    Process photo upload in Kling O1 input state.
    Photos are added to image_list (referenced as @Image1, @Image2...).
    """
    from app.core.temp_files import get_temp_file_path
    from app.utils.file_utils import resize_image_if_needed
    from app.bot.keyboards.inline import kling_o1_main_keyboard

    data = await state.get_data()
    images = data.get("kling_o1_images", [])
    video_url = data.get("kling_o1_video_url", None)

    # Check limit
    max_images = MAX_IMAGES_WITH_VIDEO if video_url else MAX_IMAGES_WITHOUT_VIDEO
    if len(images) >= max_images:
        await message.answer(
            f"⚠️ Достигнут лимит изображений ({max_images} шт.).\n"
            "Нажмите ✅ Продолжить и отправьте описание для генерации.",
            reply_markup=kling_o1_main_keyboard(has_media=True)
        )
        return

    # Download photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    temp_path = get_temp_file_path(prefix="kling_o1_img", suffix=".jpg")
    await message.bot.download_file(file.file_path, temp_path)
    resize_image_if_needed(str(temp_path), max_size_mb=2.0, max_dimension=2048)

    # Handle caption as prompt
    if message.caption and message.caption.strip():
        images.append(str(temp_path))
        await state.update_data(
            kling_o1_images=images,
            kling_o1_photo_caption_prompt=message.caption.strip()
        )
        if await is_async_enabled():
            await create_kling_o1_video_job(
                message, user, state, message.caption.strip()
            )
        else:
            await message.answer("❌ Асинхронная генерация временно отключена.")
            await clear_state_preserve_settings(state)
        return

    # No caption — add photo and show status
    images.append(str(temp_path))
    await state.update_data(kling_o1_images=images)

    img_index = len(images)
    max_remaining = max_images - img_index

    text = (
        f"✅ Фото {img_index} (@Image{img_index}) сохранено!\n\n"
    )
    if max_remaining > 0:
        text += (
            f"📸 Вы можете:\n"
            f"• Загрузить ещё фото (осталось мест: {max_remaining})\n"
            f"• Нажать ✅ Продолжить и отправить описание\n"
            f"• Или отправить текст прямо сейчас\n\n"
        )
    else:
        text += "📝 Максимум фото достигнут. Нажмите ✅ Продолжить и отправьте описание.\n\n"

    text += (
        "💡 В описании вы можете ссылаться на фото:\n"
        f"• @Image1, @Image2 — для фотографий\n"
        "• @Video1 — для видео (если загружено)"
    )

    await message.answer(text, reply_markup=kling_o1_main_keyboard(has_media=True))


@router.message(MediaState.kling_o1_waiting_for_input, F.video | F.document)
async def process_kling_o1_video(message: Message, state: FSMContext, user: User):
    """
    Process video upload in Kling O1 input state.
    Video is stored as reference URL (base or feature type).
    """
    from app.bot.keyboards.inline import kling_o1_main_keyboard
    from app.core.config import settings as bot_settings

    data = await state.get_data()
    # Check if video already uploaded
    if data.get("kling_o1_video_url"):
        await message.answer(
            "⚠️ Видео уже загружено. Нажмите ✅ Продолжить и отправьте текстовое описание.",
            reply_markup=kling_o1_main_keyboard(has_media=True)
        )
        return

    # Get video or document (for .mov files sent as document)
    if message.video:
        video = message.video
        file_size = video.file_size or 0
    elif message.document:
        video = message.document
        file_size = video.file_size or 0
    else:
        return

    # Check file size (200MB limit)
    if file_size > 200 * 1024 * 1024:
        await message.answer(
            "❌ Видео слишком большое. Максимальный размер: 200 МБ."
        )
        return

    # Get Telegram file URL
    file_info = await message.bot.get_file(video.file_id)
    video_url = _get_video_telegram_url(
        bot_settings.telegram_bot_token, file_info.file_path
    )

    await state.update_data(
        kling_o1_video_url=video_url,
        kling_o1_video_is_base=True,  # Default: video editing mode
    )

    await message.answer(
        "✅ Видео (@Video1) сохранено для редактирования!\n\n"
        "📸 Теперь вы можете:\n"
        "• Добавить дополнительные фото (элементы/картинки)\n"
        "• Нажать ✅ Продолжить и отправить описание изменений\n"
        "• Или сразу отправить текстовое описание\n\n"
        "💡 В описании используйте:\n"
        "• @Video1 — для ссылки на загруженное видео\n"
        "• @Image1, @Image2 — для ссылок на фото\n\n"
        "📋 Требования к видео:\n"
        "• Длительность: 3–10 секунд\n"
        "• Разрешение: от 720×720 до 2160×2160 px\n"
        "• FPS: 24–60\n"
        "• Формат: .mp4 или .mov",
        reply_markup=kling_o1_main_keyboard(has_media=True)
    )


# ============================================================
# Continue button → switch to prompt waiting state
# ============================================================

@router.callback_query(F.data == "kling_o1.continue")
async def kling_o1_continue(callback: CallbackQuery, state: FSMContext, user: User):
    """User pressed Continue after uploading media — switch to prompt input state."""
    from app.bot.keyboards.inline import kling_o1_main_keyboard

    data = await state.get_data()
    images = data.get("kling_o1_images", [])
    video_url = data.get("kling_o1_video_url", None)

    media_summary = _build_media_summary(images, video_url)

    await state.set_state(MediaState.kling_o1_waiting_for_prompt)

    text = (
        "✅ Медиафайлы загружены.\n\n"
        f"📁 Загружено:\n{media_summary}\n\n"
        "✍️ Теперь отправьте текстовое описание (промт).\n\n"
        "💡 В тексте вы можете ссылаться на загруженные материалы:\n"
        "• @Image1, @Image2 — для фотографий\n"
        "• @Video1 — для видео\n\n"
        "Пример: «Замените человека в @Video1 на персонажа с @Image1»"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kling_o1_main_keyboard(has_media=True))
    except Exception:
        await callback.message.answer(text, reply_markup=kling_o1_main_keyboard(has_media=True))
    await callback.answer()


@router.callback_query(F.data == "kling_o1.clear_media")
async def kling_o1_clear_media(callback: CallbackQuery, state: FSMContext, user: User):
    """Clear all uploaded media and go back to input state."""
    from app.bot.keyboards.inline import kling_o1_main_keyboard
    from app.utils.file_utils import cleanup_temp_file

    data = await state.get_data()
    images = data.get("kling_o1_images", [])
    for img_path in images:
        cleanup_temp_file(img_path)

    await state.update_data(
        kling_o1_images=[],
        kling_o1_video_url=None,
        kling_o1_video_is_base=True,
    )
    await state.set_state(MediaState.kling_o1_waiting_for_input)

    try:
        await callback.message.edit_text(
            "🗑 Все медиафайлы удалены. Отправьте новый промт, фото или видео.",
            reply_markup=kling_o1_main_keyboard(has_media=False)
        )
    except Exception:
        await callback.message.answer(
            "🗑 Все медиафайлы удалены. Отправьте новый промт, фото или видео.",
            reply_markup=kling_o1_main_keyboard(has_media=False)
        )
    await callback.answer()


# ============================================================
# STATE: kling_o1_waiting_for_prompt
# ============================================================

@router.message(MediaState.kling_o1_waiting_for_prompt, F.text)
async def process_kling_o1_prompt_text(message: Message, state: FSMContext, user: User):
    """Process text prompt after media has been uploaded."""
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return

    if await is_async_enabled():
        await create_kling_o1_video_job(message, user, state, message.text.strip())
    else:
        await message.answer("❌ Асинхронная генерация временно отключена.")
        await clear_state_preserve_settings(state)


@router.message(MediaState.kling_o1_waiting_for_prompt, F.photo)
async def process_kling_o1_prompt_extra_photo(message: Message, state: FSMContext, user: User):
    """Handle photo sent after pressing Continue — add to images and show message."""
    from app.core.temp_files import get_temp_file_path
    from app.utils.file_utils import resize_image_if_needed
    from app.bot.keyboards.inline import kling_o1_main_keyboard

    data = await state.get_data()
    images = data.get("kling_o1_images", [])
    video_url = data.get("kling_o1_video_url", None)
    max_images = MAX_IMAGES_WITH_VIDEO if video_url else MAX_IMAGES_WITHOUT_VIDEO

    if len(images) >= max_images:
        await message.answer(
            "⚠️ Максимум изображений уже загружено. Отправьте текстовое описание."
        )
        return

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    temp_path = get_temp_file_path(prefix="kling_o1_img", suffix=".jpg")
    await message.bot.download_file(file.file_path, temp_path)
    resize_image_if_needed(str(temp_path), max_size_mb=2.0, max_dimension=2048)

    if message.caption and message.caption.strip():
        images.append(str(temp_path))
        await state.update_data(kling_o1_images=images)
        if await is_async_enabled():
            await create_kling_o1_video_job(
                message, user, state, message.caption.strip()
            )
        else:
            await message.answer("❌ Асинхронная генерация временно отключена.")
            await clear_state_preserve_settings(state)
        return

    images.append(str(temp_path))
    await state.update_data(kling_o1_images=images)
    img_index = len(images)

    await message.answer(
        f"✅ Фото {img_index} (@Image{img_index}) добавлено.\n\n"
        "Отправьте текстовое описание для генерации.",
        reply_markup=kling_o1_main_keyboard(has_media=True)
    )
