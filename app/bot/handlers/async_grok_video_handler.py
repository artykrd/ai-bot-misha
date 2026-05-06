"""
Async Grok Video handler using job queue.

Creates video generation jobs for Grok Video (xAI API)
instead of waiting for completion — results are delivered
when ready without blocking the bot.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states.media import MediaState, GrokVideoSettings, clear_state_preserve_settings
from app.database.models.user import User
from app.database.database import async_session_maker
from app.database.models.system import SystemSetting
from app.services.subscription.subscription_service import SubscriptionService
from app.services.video_job_service import VideoJobService
from app.core.logger import get_logger
from app.core.exceptions import InsufficientTokensError
from app.core.billing_config import get_grok_video_tokens_cost, format_token_amount
from app.core.temp_files import get_temp_file_path
from sqlalchemy import select

logger = get_logger(__name__)

router = Router(name="async_grok_video")


async def is_async_enabled() -> bool:
    """Check if async video is enabled via feature flag."""
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


async def create_grok_video_job(
    message: Message,
    user: User,
    state: FSMContext,
) -> bool:
    """
    Create async video generation job for Grok Video.

    Returns True if job created successfully.
    """
    data = await state.get_data()
    settings_obj = GrokVideoSettings.from_dict(data)

    prompt = data.get("photo_caption_prompt") or message.text
    if not prompt:
        await message.answer("❌ Промпт не может быть пустым. Отправьте описание видео.")
        return False

    image_path = data.get("grok_video_image_path", None)

    estimated_tokens = get_grok_video_tokens_cost(settings_obj.resolution, settings_obj.duration)
    model_id = "grok-imagine-video"

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        try:
            await sub_service.check_and_use_tokens(
                user.id,
                estimated_tokens,
                model_id=model_id,
            )
        except InsufficientTokensError as e:
            from app.utils.file_utils import cleanup_temp_file
            if image_path:
                cleanup_temp_file(image_path)

            error_details = e.details
            if error_details.get("unlimited_limit_reached"):
                await message.answer(f"❌ {e.message}\n\nЛимит безлимитной подписки достигнут.")
            else:
                await message.answer(
                    f"❌ Недостаточно токенов!\n\n"
                    f"Требуется: {format_token_amount(estimated_tokens)}\n"
                    f"Доступно: {format_token_amount(error_details['available'])}"
                )

            await clear_state_preserve_settings(state)
            return False

    progress_msg = await message.answer(
        "⏳ Ваше видео Grok Video добавлено в очередь!\n\n"
        "Генерация займёт несколько минут. Мы отправим результат, как только видео будет готово.\n\n"
        "Вы можете продолжать пользоваться ботом."
    )

    try:
        async with async_session_maker() as session:
            job_service = VideoJobService(session)

            input_data = {
                "images": [image_path] if image_path else [],
                "resolution": settings_obj.resolution,
                "duration": settings_obj.duration,
                "aspect_ratio": settings_obj.aspect_ratio,
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
                units=float(settings_obj.duration),
                request_type="video",
            )

            job = await job_service.create_job(
                user_id=user.id,
                provider="grok_video",
                model_id=model_id,
                prompt=prompt,
                input_data=input_data,
                chat_id=message.chat.id,
                tokens_cost=estimated_tokens,
                progress_message_id=progress_msg.message_id,
                ai_request_id=ai_request_id,
            )

            logger.info(
                "grok_video_job_created",
                user_id=user.id,
                job_id=job.id,
                resolution=settings_obj.resolution,
                duration=settings_obj.duration,
                tokens=estimated_tokens,
            )

    except Exception as e:
        logger.error("grok_video_job_creation_failed", error=str(e), user_id=user.id)

        async with async_session_maker() as session:
            sub_service = SubscriptionService(session)
            await sub_service.rollback_tokens(user.id, estimated_tokens)

        await progress_msg.edit_text(
            f"❌ Ошибка создания задачи: {str(e)[:200]}\n\nТокены возвращены."
        )
        return False

    finally:
        await clear_state_preserve_settings(state)

    return True


@router.message(MediaState.grok_video_waiting_for_prompt, F.text)
async def process_grok_video_text(message: Message, state: FSMContext, user: User):
    """Handle text prompt for Grok Video generation."""
    if message.text and message.text.startswith("/"):
        await clear_state_preserve_settings(state)
        return

    if await is_async_enabled():
        await create_grok_video_job(message, user, state)
    else:
        await message.answer("❌ Асинхронная генерация временно отключена. Попробуйте позже.")
        await clear_state_preserve_settings(state)


@router.message(MediaState.grok_video_waiting_for_prompt, F.photo)
async def process_grok_video_photo(message: Message, state: FSMContext, user: User):
    """Handle photo (image-to-video) for Grok Video."""
    from app.utils.file_utils import resize_image_if_needed

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    temp_path = get_temp_file_path(prefix="grok_video_img", suffix=".jpg")
    await message.bot.download_file(file.file_path, temp_path)
    resize_image_if_needed(str(temp_path), max_size_mb=2.0, max_dimension=2048)

    if message.caption and message.caption.strip():
        await state.update_data(
            grok_video_image_path=str(temp_path),
            photo_caption_prompt=message.caption.strip(),
        )
        if await is_async_enabled():
            await create_grok_video_job(message, user, state)
        else:
            await message.answer("❌ Асинхронная генерация временно отключена.")
            await clear_state_preserve_settings(state)
    else:
        await state.update_data(grok_video_image_path=str(temp_path))
        await message.answer(
            "✅ Фото сохранено!\n\n"
            "📝 Теперь отправьте текстовое описание того, что должно происходить в видео."
        )
