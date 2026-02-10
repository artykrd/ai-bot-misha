"""
Sora 2 callback endpoint.

Kie.ai sends POST requests here when video generation completes or fails.
Handler is idempotent — duplicate callbacks are safely ignored.
"""
import json
from datetime import datetime, timezone

import aiohttp
from aiogram.exceptions import TelegramBadRequest
from fastapi import APIRouter, Request, HTTPException
from pathlib import Path

from app.core.config import settings
from app.core.logger import get_logger
from app.database.database import async_session_maker
from app.services.subscription.subscription_service import SubscriptionService
from app.services.video_job_service import VideoJobService

logger = get_logger(__name__)

router = APIRouter()


@router.post("/api/sora_callback")
async def sora_callback(request: Request):
    """
    Callback endpoint for Kie.ai Sora 2 video generation.

    Expected JSON structure from Kie.ai:
    {
        "code": 200,
        "data": {
            "taskId": "...",
            "state": "success" | "fail",
            "resultJson": "{ \"resultUrls\": [...] }",
            "failMsg": "..."
        }
    }
    """
    try:
        body = await request.json()
    except Exception:
        logger.error("sora_callback_invalid_json")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logger.info(
        "sora_callback_received",
        body_keys=list(body.keys()) if isinstance(body, dict) else [],
        code=body.get("code") if isinstance(body, dict) else None,
    )

    # Extract task data — handle both flat and nested formats
    if isinstance(body, dict) and "data" in body:
        task_data = body.get("data", {})
    else:
        task_data = body if isinstance(body, dict) else {}

    task_id = task_data.get("taskId")
    state = task_data.get("state", "unknown")

    if not task_id:
        logger.error("sora_callback_no_task_id", body=body)
        raise HTTPException(status_code=400, detail="No taskId in callback")

    logger.info(
        "sora_callback_parsed",
        task_id=task_id,
        state=state,
    )

    # Find job in database
    async with async_session_maker() as session:
        job_service = VideoJobService(session)
        job = await job_service.get_job_by_task_id(task_id)

        if not job:
            logger.warning("sora_callback_job_not_found", task_id=task_id)
            return {"status": "ok", "message": "Job not found, possibly expired"}

        # Idempotent: if already completed/failed, skip
        if job.is_finished:
            logger.info(
                "sora_callback_already_finished",
                task_id=task_id,
                job_id=job.id,
                status=job.status,
            )
            return {"status": "ok", "message": "Already processed"}

        if state == "success":
            await _handle_success(session, job_service, job, task_data)
        elif state == "fail":
            await _handle_failure(session, job_service, job, task_data)
        else:
            # Intermediate state (pending, processing) — just log
            logger.info(
                "sora_callback_intermediate_state",
                task_id=task_id,
                state=state,
            )

    return {"status": "ok"}


async def _handle_success(session, job_service, job, task_data: dict):
    """Handle successful video generation callback."""
    from aiogram.types import FSInputFile
    from app.bot.bot_instance import bot
    from app.bot.utils.notifications import format_generation_message, CONTENT_TYPES
    from app.bot.utils.notifications import MODEL_ACTIONS, create_action_keyboard

    task_id = task_data.get("taskId", "")

    # Parse resultJson
    result_json_str = task_data.get("resultJson", "{}")
    try:
        result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
    except (json.JSONDecodeError, TypeError):
        result_json = {}

    result_urls = result_json.get("resultUrls", [])
    if not result_urls:
        logger.error("sora_callback_no_result_urls", task_id=task_id, result_json=result_json)
        await _handle_failure(session, job_service, job, {
            "taskId": task_id,
            "failMsg": "No result URLs in callback response"
        })
        return

    video_url = result_urls[0]

    # Download video
    storage_path = Path(settings.storage_path) / "videos"
    storage_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sora_{timestamp}_{task_id[:8]}.mp4"
    file_path = storage_path / filename

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(video_url) as response:
                if response.status != 200:
                    raise Exception(f"Download failed: HTTP {response.status}")
                with open(file_path, 'wb') as f:
                    f.write(await response.read())

        logger.info("sora_callback_video_downloaded", task_id=task_id, path=str(file_path))
    except Exception as e:
        logger.error("sora_callback_download_failed", task_id=task_id, error=str(e))
        await _handle_failure(session, job_service, job, {
            "taskId": task_id,
            "failMsg": f"Video download failed: {e}"
        })
        return

    # Mark job completed
    await job_service.update_job_status(
        job.id,
        "completed",
        video_path=str(file_path),
        task_id=task_id,
    )

    # Commit tokens (no-op — already deducted during reservation)
    sub_service = SubscriptionService(session)
    await sub_service.commit_tokens(job.user_id, job.tokens_cost)

    # Get remaining tokens for user message
    user_tokens = await sub_service.get_available_tokens(job.user_id)

    # Send video to user
    try:
        model_display = job.input_data.get("quality_text", "Stable")
        caption = format_generation_message(
            content_type=CONTENT_TYPES["video"],
            model_name=f"Sora 2 {model_display}",
            tokens_used=job.tokens_cost,
            user_tokens=user_tokens,
            prompt=job.prompt,
        )

        builder = create_action_keyboard(
            action_text=MODEL_ACTIONS["sora"]["text"],
            action_callback=MODEL_ACTIONS["sora"]["callback"],
            file_path=str(file_path),
            file_type="video",
        )

        video_file = FSInputFile(str(file_path))
        await bot.send_video(
            chat_id=job.chat_id,
            video=video_file,
            caption=caption,
            reply_markup=builder.as_markup(),
        )

        # Delete progress message
        if job.progress_message_id:
            try:
                await bot.delete_message(chat_id=job.chat_id, message_id=job.progress_message_id)
            except TelegramBadRequest as e:
                # Ignore expected errors when message can't be deleted
                if "message can't be deleted" not in str(e) and "message to delete not found" not in str(e):
                    logger.warning("sora_delete_message_failed", error=str(e), job_id=job.id)
            except Exception as e:
                logger.warning("sora_delete_message_error", error=str(e), job_id=job.id)

        logger.info(
            "sora_task_success",
            task_id=task_id,
            job_id=job.id,
            user_id=job.user_id,
            tokens=job.tokens_cost,
        )
    except Exception as e:
        logger.error(
            "sora_callback_send_failed",
            task_id=task_id,
            error=str(e),
            user_id=job.user_id,
        )


async def _handle_failure(session, job_service, job, task_data: dict):
    """Handle failed video generation callback."""
    from app.bot.bot_instance import bot

    task_id = task_data.get("taskId", "")
    fail_msg = task_data.get("failMsg", "Unknown error")

    # Mark job failed
    await job_service.update_job_status(
        job.id,
        "failed",
        error_message=fail_msg,
    )

    # Rollback reserved tokens
    sub_service = SubscriptionService(session)
    await sub_service.rollback_tokens(job.user_id, job.tokens_cost)

    # Notify user
    try:
        if job.progress_message_id:
            await bot.edit_message_text(
                chat_id=job.chat_id,
                message_id=job.progress_message_id,
                text=f"❌ Ошибка генерации Sora 2:\n{fail_msg}\n\n"
                     f"💰 Токены возвращены на баланс.",
                parse_mode=None,
            )
        else:
            await bot.send_message(
                chat_id=job.chat_id,
                text=f"❌ Ошибка генерации Sora 2:\n{fail_msg}\n\n"
                     f"💰 Токены возвращены на баланс.",
            )
    except Exception as e:
        logger.error("sora_callback_notify_failed", error=str(e), user_id=job.user_id)

    logger.info(
        "sora_task_fail",
        task_id=task_id,
        job_id=job.id,
        user_id=job.user_id,
        fail_msg=fail_msg,
    )
