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
        url = f"{self.BASE_URL}/music/generate"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build payload
        payload = {
            "prompt": prompt,
            "make_instrumental": kwargs.get("instrumental", False),
            "wait_audio": False  # Use async mode
        }

        # Optional parameters
        if "custom_mode" in kwargs and kwargs["custom_mode"]:
            payload["custom_mode"] = True
            if "tags" in kwargs:
                payload["tags"] = kwargs["tags"]
            if "title" in kwargs:
                payload["title"] = kwargs["title"]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Suno API error: {response.status} - {error_text}")

                data = await response.json()
                # Return list of task IDs
                if "data" in data and isinstance(data["data"], list):
                    return [task["id"] for task in data["data"]]
                else:
                    raise Exception("Unexpected API response format")

    async def _poll_generation_status(
        self,
        task_ids: List[str],
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 300,  # 5 minutes
        poll_interval: int = 5  # 5 seconds
    ) -> List[str]:
        """
        Poll generation status until complete.

        Returns:
            List of audio URLs
        """
        start_time = time.time()
        last_status = None

        while True:
            # Check timeout
            if time.time() - start_time > max_wait_time:
                raise Exception("Music generation timeout")

            try:
                # Query all task IDs
                audio_urls = []
                all_completed = True

                for task_id in task_ids:
                    url = f"{self.BASE_URL}/music/{task_id}"
                    headers = {
                        "Authorization": f"Bearer {self.api_key}"
                    }

                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                raise Exception(f"Status check failed: {response.status} - {error_text}")

                            data = await response.json()

                            if "data" in data:
                                task_data = data["data"]
                                status = task_data.get("status", "unknown")

                                # Update user if status changed
                                if status != last_status and progress_callback:
                                    if status == "submitted":
                                        await progress_callback("⏳ Задача в очереди...")
                                    elif status == "processing":
                                        await progress_callback("🎼 Создаю музыку...")
                                    elif status == "complete":
                                        await progress_callback("🎵 Почти готово...")

                                last_status = status

                                # Check if this task is complete
                                if status == "complete":
                                    audio_url = task_data.get("audio_url")
                                    if audio_url:
                                        audio_urls.append(audio_url)
                                else:
                                    all_completed = False

                # If all tasks completed, return URLs
                if all_completed and audio_urls:
                    return audio_urls

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error("suno_poll_error", error=str(e))
                raise
