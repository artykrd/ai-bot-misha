"""
Suno AI music generation service via sunoapi.org.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable, List

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.audio.base import BaseAudioProvider, AudioResponse

logger = get_logger(__name__)


class SunoService(BaseAudioProvider):
    """Suno API integration for music generation."""

    BASE_URL = "https://api.sunoapi.org/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.suno_api_key)
        if not self.api_key:
            logger.warning("suno_api_key_missing")

    async def generate_audio(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> AudioResponse:
        """
        Generate music using Suno AI.

        Args:
            prompt: Music generation prompt/description
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters (custom_mode, tags, title, etc.)

        Returns:
            AudioResponse with audio path or error
        """
        start_time = time.time()

        if not self.api_key:
            return AudioResponse(
                success=False,
                error="Suno API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Notify user that generation is starting
            if progress_callback:
                await progress_callback("🎵 Начинаю создание музыки с Suno AI...")

            # Step 1: Create generation request
            task_ids = await self._create_generation(prompt, **kwargs)
            logger.info(
                "suno_generation_created",
                task_ids=task_ids
            )

            # Step 2: Poll for completion
            audio_urls = await self._poll_generation_status(
                task_ids,
                progress_callback
            )

            # Step 3: Download audio files (take first one if multiple)
            if progress_callback:
                await progress_callback("📥 Скачиваю аудио...")

            # Download the first generated track
            filename = self._generate_filename("mp3")
            audio_path = await self._download_file(audio_urls[0], filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Музыка готова!")

            logger.info(
                "suno_audio_generated",
                path=audio_path,
                time=processing_time
            )

            return AudioResponse(
                success=True,
                audio_path=audio_path,
                processing_time=processing_time,
                metadata={
                    "provider": "suno",
                    "task_ids": task_ids,
                    "tracks_count": len(audio_urls)
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("suno_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return AudioResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation(self, prompt: str, **kwargs) -> List[str]:
        """Create music generation request and return task IDs."""
        url = f"{self.BASE_URL}/generate"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build payload according to Suno API documentation
        payload = {
            "prompt": prompt,
            "customMode": kwargs.get("custom_mode", True),
            "instrumental": kwargs.get("instrumental", False),
            "model": kwargs.get("model", "V4"),  # V4, V4_5, V4_5PLUS, V4_5ALL, V5 (V4 - оптимальное соотношение цена/качество)
            # callBackUrl is REQUIRED by API (we use polling but API needs this)
            "callBackUrl": kwargs.get("callBackUrl", "https://httpbin.org/post")
        }

        # Optional parameters for custom mode
        if payload["customMode"]:
            if "style" in kwargs:
                payload["style"] = kwargs["style"]
            if "title" in kwargs:
                payload["title"] = kwargs["title"]

        # Other optional parameters
        if "negativeTags" in kwargs:
            payload["negativeTags"] = kwargs["negativeTags"]
        if "vocalGender" in kwargs:
            payload["vocalGender"] = kwargs["vocalGender"]
        if "styleWeight" in kwargs:
            payload["styleWeight"] = kwargs["styleWeight"]
        if "weirdnessConstraint" in kwargs:
            payload["weirdnessConstraint"] = kwargs["weirdnessConstraint"]
        if "audioWeight" in kwargs:
            payload["audioWeight"] = kwargs["audioWeight"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Suno API error: {response.status} - {error_text}")

                data = await response.json()
                # Response format: {"code": 200, "msg": "success", "data": {"taskId": "..."}}
                if data.get("code") == 200 and "data" in data:
                    task_id = data["data"].get("taskId")
                    if task_id:
                        return [task_id]  # Return as list for compatibility
                    else:
                        raise Exception("No taskId in response")
                else:
                    error_msg = data.get("msg", "Unknown error")
                    raise Exception(f"Suno API error: {error_msg}")

    async def _poll_generation_status(
        self,
        task_ids: List[str],
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,  # 10 minutes
        poll_interval: int = 5,  # 5 seconds
        max_iterations: int = 120  # Maximum 120 iterations (10 minutes at 5s interval)
    ) -> List[str]:
        """
        Poll generation status until complete.

        Returns:
            List of audio URLs
        """
        # Terminal statuses that indicate task completion with audio available
        # NOTE: Based on API behavior and logs analysis:
        # - SUCCESS: Full completion with audio URLs available
        # - COMPLETED: Alternative completion status
        #
        # Non-terminal statuses (continue polling):
        # - PENDING: Task queued
        # - TEXT_SUCCESS: Lyrics generated, audio not ready yet
        # - FIRST_SUCCESS: First track processing, audio URLs not available yet
        #
        # IMPORTANT: TEXT_SUCCESS and FIRST_SUCCESS are intermediate states.
        # Audio URLs appear only in SUCCESS status. Do not treat them as terminal.
        TERMINAL_STATUSES = {"SUCCESS", "COMPLETED"}

        # Error statuses that should stop polling immediately
        ERROR_STATUSES = {"FAILED", "ERROR", "CANCELLED"}

        start_time = time.time()
        last_status = None
        same_status_count = 0
        iteration = 0

        while True:
            iteration += 1

            # Check max iterations
            if iteration > max_iterations:
                raise Exception(f"Music generation exceeded maximum iterations ({max_iterations})")

            # Check timeout
            if time.time() - start_time > max_wait_time:
                raise Exception(f"Music generation timeout ({max_wait_time}s)")

            try:
                # Query all task IDs
                audio_urls = []
                all_completed = True
                all_terminal = True

                for task_id in task_ids:
                    url = f"{self.BASE_URL}/generate/record-info"
                    headers = {
                        "Authorization": f"Bearer {self.api_key}"
                    }

                    params = {
                        "taskId": task_id
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, params=params) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                raise Exception(f"Status check failed: {response.status} - {error_text}")

                            data = await response.json()

                            # Log raw response for debugging (more verbose for terminal statuses)
                            status_preview = data.get("data", {}).get("status", "").upper() if isinstance(data.get("data"), dict) else ""
                            is_terminal_status = status_preview in {"SUCCESS", "COMPLETED"}

                            logger.info(
                                "suno_poll_response",
                                task_id=task_id,
                                response_code=data.get("code"),
                                has_data="data" in data,
                                raw_data=str(data) if is_terminal_status else str(data)[:500]  # Full data for terminal statuses
                            )

                            # Response format: {"code": 200, "msg": "success", "data": {"taskId": "...", "status": "...", "response": {"sunoData": [...]}}}
                            if data.get("code") == 200 and "data" in data:
                                task_data = data["data"]
                                status = task_data.get("status", "UNKNOWN").upper()

                                # Log detailed status info
                                logger.info(
                                    "suno_task_status",
                                    task_id=task_id,
                                    status=status,
                                    has_response="response" in task_data,
                                    elapsed_time=int(time.time() - start_time),
                                    iteration=iteration
                                )

                                # Check for error statuses
                                if status in ERROR_STATUSES:
                                    error_msg = task_data.get("error") or task_data.get("failReason") or "Unknown error"
                                    raise Exception(f"Generation failed with status {status}: {error_msg}")

                                # Update user if status changed
                                if status != last_status and progress_callback:
                                    if status == "PENDING":
                                        await progress_callback("⏳ Задача в очереди...")
                                    elif status in {"TEXT_SUCCESS", "FIRST_SUCCESS"}:
                                        await progress_callback("🎼 Создаю музыку...")
                                    elif status == "SUCCESS":
                                        await progress_callback("🎵 Почти готово...")
                                    else:
                                        # Log unknown status (might be new API status)
                                        logger.warning("suno_unknown_status", status=status, task_id=task_id)

                                # Track status changes for stuck detection
                                if status == last_status:
                                    same_status_count += 1
                                else:
                                    same_status_count = 0
                                    last_status = status

                                # Check if this task reached terminal status
                                if status in TERMINAL_STATUSES:
                                    # Try to extract audio URLs from response
                                    response_data = task_data.get("response", {})
                                    suno_data = response_data.get("sunoData", [])

                                    logger.info(
                                        "suno_processing_results",
                                        task_id=task_id,
                                        status=status,
                                        suno_data_count=len(suno_data) if suno_data else 0,
                                        has_suno_data=bool(suno_data)
                                    )

                                    if suno_data:
                                        for idx, track in enumerate(suno_data):
                                            audio_url = track.get("audioUrl") or track.get("audio_url")
                                            logger.info(
                                                "suno_track_url",
                                                task_id=task_id,
                                                track_index=idx,
                                                has_audio_url=bool(audio_url),
                                                audio_url=audio_url[:100] if audio_url else None
                                            )
                                            if audio_url:
                                                audio_urls.append(audio_url)

                                    # Task reached terminal status
                                    # all_completed stays True (will be set to False only for non-terminal statuses)
                                else:
                                    # Not a terminal status yet, keep polling
                                    all_completed = False
                                    all_terminal = False
                            else:
                                # API returned error or unexpected format
                                logger.error(
                                    "suno_api_error_response",
                                    task_id=task_id,
                                    code=data.get("code"),
                                    msg=data.get("msg"),
                                    has_data="data" in data
                                )
                                raise Exception(f"API error: {data.get('msg', 'Unknown error')}")

                # Check completion status
                logger.info(
                    "suno_poll_iteration",
                    all_completed=all_completed,
                    all_terminal=all_terminal,
                    audio_urls_count=len(audio_urls),
                    elapsed_time=int(time.time() - start_time),
                    iteration=iteration,
                    same_status_count=same_status_count
                )

                # If all tasks reached terminal status
                if all_terminal:
                    if audio_urls:
                        logger.info("suno_generation_complete", urls_count=len(audio_urls))
                        return audio_urls
                    else:
                        # Terminal status reached but no audio URLs found
                        # This might indicate API issue or different response structure
                        raise Exception(
                            f"Generation reached terminal status ({last_status}) "
                            f"but no audio URLs were found in response. "
                            f"Check API documentation or contact support."
                        )

                # Protection against stuck polling (same status for too long)
                # Different thresholds for different statuses:
                # - PENDING: 240s (API might take time to start processing)
                # - Processing statuses: 360s (music generation takes time)
                # - Unknown statuses: 120s (fail fast for unexpected states)
                if last_status == "PENDING":
                    max_stuck_iterations = 48  # 48 * 5s = 240 seconds
                elif last_status in {"TEXT_SUCCESS", "FIRST_SUCCESS"}:
                    max_stuck_iterations = 72  # 72 * 5s = 360 seconds
                else:
                    max_stuck_iterations = 24  # 24 * 5s = 120 seconds

                if same_status_count > max_stuck_iterations:
                    logger.warning(
                        "suno_status_stuck",
                        status=last_status,
                        stuck_iterations=same_status_count,
                        max_allowed=max_stuck_iterations
                    )
                    raise Exception(
                        f"Generation stuck at status {last_status} "
                        f"for {same_status_count * poll_interval} seconds "
                        f"(max allowed: {max_stuck_iterations * poll_interval}s)"
                    )

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error("suno_poll_error", error=str(e), iteration=iteration)
                raise
