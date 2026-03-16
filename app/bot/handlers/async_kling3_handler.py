"""
Async Kling 3.0 video handler using job queue.

Creates video generation jobs for Kling 3.0 (via Kie.ai API)
instead of waiting for completion, allowing the bot to handle
concurrent requests without blocking.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states.media import MediaState, Kling3Settings, clear_state_preserve_settings
from app.database.models.user import User
from app.database.database import async_session_maker
from app.database.models.system import SystemSetting
from app.services.subscription.subscription_service import SubscriptionService
from app.services.video_job_service import VideoJobService
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.core.billing_config import get_kling3_tokens_cost
from sqlalchemy import select

logger = get_logger(__name__)

router = Router(name="async_kling3")


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


async def create_kling3_video_job(
    message: Message,
    user: User,
    state: FSMContext
) -> bool:
    """
    Create async video generation job for Kling 3.0.

    Returns:
        True if job created successfully, False otherwise
    """
    data = await state.get_data()
    kling3_settings = Kling3Settings.from_dict(data)

    # Get prompt
    prompt = data.get("photo_caption_prompt") or message.text

    # Auto-translate if enabled
    if kling3_settings.auto_translate and prompt:
        try:
            from app.services.ai.openai_service import OpenAIService
            openai_service = OpenAIService()
            translated = await openai_service.translate_to_english(prompt)
            if translated:
                prompt = translated
        except Exception as e:
            logger.warning("kling3_translate_failed", error=str(e))

    # Get images
    images = data.get("kling3_images", [])
    single_image = data.get("image_path", None)
    if single_image and single_image not in images:
        images = [single_image]

    # Calculate tokens
    estimated_tokens = get_kling3_tokens_cost(kling3_settings.mode, kling3_settings.duration)

    # Model ID for limits check
    model_id = f"kling3-{kling3_settings.mode}"

    # Check and use tokens
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            subscription = await sub_service.check_and_use_tokens(
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

    # Send "in queue" message
    progress_msg = await message.answer(
        "⏳ Ваше видео Kling 3.0 добавлено в очередь на генерацию!\n\n"
        "Мы отправим вам результат, как только он будет готов. "
        "Это может занять от 5 до 15 минут.\n\n"
        "Вы можете продолжать пользоваться ботом, пока видео генерируется."
    )

    try:
        async with async_session_maker() as session:
            job_service = VideoJobService(session)

            input_data = {
                "images": images,
                "duration": kling3_settings.duration,
                "aspect_ratio": kling3_settings.aspect_ratio,
                "mode": kling3_settings.mode,
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
                provider="kling3",
                model_id="kling-3.0/video",
                prompt=prompt,
                input_data=input_data,
                chat_id=message.chat.id,
                tokens_cost=estimated_tokens,
                progress_message_id=progress_msg.message_id,
                ai_request_id=ai_request_id
            )

            logger.info(
                "kling3_video_job_created",
                user_id=user.id,
                job_id=job.id,
                model=model_id,
                tokens=estimated_tokens,
                mode=kling3_settings.mode,
                duration=kling3_settings.duration,
            )

    except Exception as e:
        logger.error("kling3_job_creation_failed", error=str(e), user_id=user.id)

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


@router.message(MediaState.kling3_waiting_for_prompt, F.text)
async def process_kling3_text_async(message: Message, state: FSMContext, user: User):
    """Process Kling 3.0 text prompt with async job queue."""
    if message.text and message.text.startswith('/'):
        await clear_state_preserve_settings(state)
        return

    if await is_async_enabled():
        logger.info("using_async_kling3", user_id=user.id)
        await create_kling3_video_job(message, user, state)
    else:
        logger.info("async_disabled_for_kling3", user_id=user.id)
        await message.answer("❌ Асинхронная генерация временно отключена. Попробуйте позже.")
        await clear_state_preserve_settings(state)


@router.message(MediaState.kling3_waiting_for_prompt, F.photo)
async def process_kling3_photo_async(message: Message, state: FSMContext, user: User):
    """Process Kling 3.0 photo with async job queue."""
    from app.core.temp_files import get_temp_file_path
    from app.utils.file_utils import resize_image_if_needed

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    temp_path = get_temp_file_path(prefix="kling3_image", suffix=".jpg")
    await message.bot.download_file(file.file_path, temp_path)

    resize_image_if_needed(str(temp_path), max_size_mb=2.0, max_dimension=2048)

    data = await state.get_data()
    kling3_images = data.get("kling3_images", [])
    kling3_images.append(str(temp_path))

    if message.caption and message.caption.strip():
        # Has prompt - generate immediately
        await state.update_data(
            kling3_images=kling3_images,
            photo_caption_prompt=message.caption.strip()
        )

        if await is_async_enabled():
            await create_kling3_video_job(message, user, state)
        else:
            await message.answer("❌ Асинхронная генерация временно отключена.")
            await clear_state_preserve_settings(state)
    else:
        # No prompt - ask for more
        await state.update_data(kling3_images=kling3_images)

        photos_count = len(kling3_images)

        if photos_count < 2:
            await message.answer(
                f"✅ Фото {photos_count} сохранено!\n\n"
                f"📸 Вы можете:\n"
                f"• Загрузить ещё одно фото (Kling 3.0 поддерживает до 2 изображений)\n"
                f"• Отправить текстовый промпт для начала генерации"
            )
        else:
            await message.answer(
                f"✅ Фото сохранено! (максимум 2)\n\n"
                f"📝 Теперь отправьте текстовый промпт для генерации видео."
            )
