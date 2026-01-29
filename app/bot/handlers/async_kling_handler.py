"""
Async Kling video handler using job queue.

This handler creates video generation jobs instead of waiting for completion,
allowing bot to handle 100+ concurrent requests without blocking.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states.media import MediaState
from app.database.models.user import User
from app.database.database import async_session_maker
from app.database.models.system import SystemSetting
from app.services.subscription.subscription_service import SubscriptionService
from app.services.video_job_service import VideoJobService
from app.services.logging import log_ai_operation_background
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.core.billing_config import get_kling_tokens_cost, get_kling_api_model
from app.bot.states.media import KlingSettings
from sqlalchemy import select

logger = get_logger(__name__)

router = Router(name="async_kling")


async def is_async_enabled() -> bool:
    """Check if async video is enabled."""
    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(SystemSetting).where(SystemSetting.key == "async_video_enabled")
            )
            setting = result.scalar_one_or_none()
            if not setting:
                return True  # Default enabled
            return setting.value.lower() in ("true", "1", "yes")
    except Exception:
        return True  # Default enabled


async def create_kling_video_job(
    message: Message,
    user: User,
    state: FSMContext
) -> bool:
    """
    Create async video generation job for Kling.

    Returns:
        True if job created successfully, False otherwise
    """
    # Get state data
    data = await state.get_data()
    kling_settings = KlingSettings.from_dict(data)

    # Get prompt
    prompt = data.get("photo_caption_prompt") or message.text

    # Get images
    images = data.get("kling_images", [])
    single_image = data.get("image_path", None)
    if single_image and single_image not in images:
        images = [single_image]

    # Calculate tokens
    estimated_tokens = get_kling_tokens_cost(kling_settings.version, kling_settings.duration)

    # Model ID for limits check
    model_id = f"kling-{kling_settings.version}"

    # Check and use tokens (with limits check)
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            subscription = await sub_service.check_and_use_tokens(
                user.id,
                estimated_tokens,
                model_id=model_id
            )
        except InsufficientTokensError as e:
            # Clean up images
            from app.utils.file_utils import cleanup_temp_file
            for img_path in images:
                cleanup_temp_file(img_path)

            error_details = e.details
            if error_details.get("unlimited_limit_reached"):
                # Unlimited limit reached
                await message.answer(
                    f"❌ {e.message}\n\n"
                    "Лимит безлимитной подписки достигнут."
                )
            else:
                # Regular insufficient tokens
                await message.answer(
                    f"❌ Недостаточно токенов!\n\n"
                    f"Требуется: {estimated_tokens:,} токенов\n"
                    f"Доступно: {error_details['available']:,} токенов"
                )

            await state.clear()
            return False

    # Send "in queue" message
    progress_msg = await message.answer(
        "⏳ Ваше видео добавлено в очередь на генерацию!\n\n"
        "Мы отправим вам результат, как только он будет готов. "
        "Это может занять несколько минут.\n\n"
        "Вы можете продолжать пользоваться ботом, пока видео генерируется."
    )

    try:
        # Create video generation job
        async with async_session_maker() as session:
            job_service = VideoJobService(session)

            # Prepare input data
            input_data = {
                "images": images,
                "duration": kling_settings.duration,
                "aspect_ratio": kling_settings.aspect_ratio,
                "version": kling_settings.version,
            }

            # Get API model name
            api_model = get_kling_api_model(kling_settings.version)

            # Create AI request for tracking (pending)
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

            # Create job
            job = await job_service.create_job(
                user_id=user.id,
                provider="kling",
                model_id=api_model,
                prompt=prompt,
                input_data=input_data,
                chat_id=message.chat.id,
                tokens_cost=estimated_tokens,
                progress_message_id=progress_msg.message_id,
                ai_request_id=ai_request_id
            )

            logger.info(
                "kling_video_job_created",
                user_id=user.id,
                job_id=job.id,
                model=model_id,
                tokens=estimated_tokens
            )

    except Exception as e:
        logger.error("kling_job_creation_failed", error=str(e), user_id=user.id)

        # Refund tokens
        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            subscription = await sub_service.get_active_subscription(user.id)
            if subscription and not subscription.is_unlimited:
                subscription.tokens_used = max(0, subscription.tokens_used - estimated_tokens)
                await session.commit()

        await progress_msg.edit_text(
            f"❌ Ошибка создания задачи: {str(e)[:200]}\n\n"
            "Токены возвращены на ваш счёт."
        )

        return False

    finally:
        await state.clear()

    return True


@router.message(MediaState.kling_waiting_for_prompt, F.text)
async def process_kling_text_async(message: Message, state: FSMContext, user: User):
    """Process Kling text prompt with async job queue (if enabled)."""
    # CRITICAL FIX: Ignore commands
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    # Check if async is enabled
    if await is_async_enabled():
        logger.info("using_async_kling", user_id=user.id)
        await create_kling_video_job(message, user, state)
    else:
        # Fall back to sync flow
        logger.info("using_sync_kling_fallback", user_id=user.id)
        from app.bot.handlers.media_handler import process_kling_video
        await process_kling_video(message, user, state, is_effects=False)


@router.message(MediaState.kling_waiting_for_prompt, F.photo)
async def process_kling_photo_async(message: Message, state: FSMContext, user: User):
    """Process Kling photo with async job queue (if enabled)."""
    # Download and save photo first
    from app.utils.file_utils import get_temp_file_path, resize_image_if_needed

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    temp_path = get_temp_file_path(prefix="kling_image", suffix=".jpg")
    await message.bot.download_file(file.file_path, temp_path)

    # Resize if needed
    resize_image_if_needed(str(temp_path), max_size_mb=2.0, max_dimension=2048)

    # Add to collected images
    data = await state.get_data()
    kling_images = data.get("kling_images", [])
    kling_images.append(str(temp_path))

    # Check caption for prompt
    if message.caption and message.caption.strip():
        # Has prompt - generate immediately
        await state.update_data(
            kling_images=kling_images,
            photo_caption_prompt=message.caption.strip()
        )

        if await is_async_enabled():
            await create_kling_video_job(message, user, state)
        else:
            from app.bot.handlers.media_handler import process_kling_video
            await process_kling_video(message, user, state, is_effects=False)
    else:
        # No prompt - ask for more
        await state.update_data(kling_images=kling_images)

        photos_count = len(kling_images)
        data = await state.get_data()
        kling_settings = KlingSettings.from_dict(data)

        if kling_settings.version == "2.5" and photos_count < 2:
            await message.answer(
                f"✅ Фото {photos_count} сохранено!\n\n"
                f"📸 Вы можете:\n"
                f"• Загрузить ещё одно фото (версия 2.5 поддерживает до 2 изображений)\n"
                f"• Отправить текстовый промпт для начала генерации"
            )
        else:
            await message.answer(
                f"✅ Фото сохранено!\n\n"
                f"📝 Теперь отправьте текстовый промпт для генерации видео."
            )
