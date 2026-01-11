"""
Hailuo (MiniMax) AI video generation service using official MiniMax API.
Documentation: https://platform.minimax.io/docs
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable
import os
import base64

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class HailuoService(BaseVideoProvider):
    """
    Hailuo (MiniMax) official API integration for video generation.

    Supports:
    - Text-to-Video
    - Image-to-Video
    - First & Last Frame Video Generation

    Models:
    - MiniMax-Hailuo-2.3 (latest, best quality)
    - MiniMax-Hailuo-2.3-Fast (faster image-to-video)
    - MiniMax-Hailuo-02 (higher resolution support)
    """

    BASE_URL = "https://api.minimax.io"

    def __init__(self, api_key: Optional[str] = None):
        # Use dedicated Hailuo API key
        super().__init__(api_key or getattr(settings, 'hailuo_api_key', None))
        if not self.api_key:
            logger.warning("hailuo_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Hailuo AI (MiniMax API).

        Args:
            prompt: Video generation prompt
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - image_path: Path to first frame image for image-to-video (optional)
                - model: Model to use (default: "MiniMax-Hailuo-2.3")
                - duration: Video duration in seconds (default: 6)
                - resolution: Video resolution (default: "768P")
                - prompt_optimizer: Auto-optimize prompt (default: True)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Hailuo API ключ не настроен. Добавьте HAILUO_API_KEY в .env файл.",
                processing_time=time.time() - start_time
            )

        try:
            # Get parameters
            image_path = kwargs.get("image_path", None)
            model = kwargs.get("model", "MiniMax-Hailuo-2.3")
            duration = kwargs.get("duration", 6)
            resolution = kwargs.get("resolution", "768P")
            prompt_optimizer = kwargs.get("prompt_optimizer", True)

            # Notify user that generation is starting
            if progress_callback:
                mode = "изображения в видео" if image_path else "текста в видео"
                await progress_callback(f"🎬 Начинаю генерацию видео из {mode} с Hailuo AI ({model})...")

            # Step 1: Create generation task
            task_id = await self._create_generation_task(
                prompt=prompt,
                image_path=image_path,
                model=model,
                duration=duration,
                resolution=resolution,
                prompt_optimizer=prompt_optimizer
            )

            logger.info(
                "hailuo_task_created",
                task_id=task_id,
                model=model,
                has_image=bool(image_path)
            )

            # Step 2: Poll for completion
            file_id = await self._poll_generation_status(
                task_id,
                progress_callback
            )

            # Step 3: Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_video(file_id, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "hailuo_video_generated",
                path=video_path,
                time=processing_time,
                model=model
            )

            # Стоимость Hailuo: 90,000 токенов за видео
            tokens_used = 90000

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                tokens_used=tokens_used,
                metadata={
                    "provider": "hailuo",
                    "model": model,
                    "task_id": task_id,
                    "file_id": file_id,
                    "duration": duration,
                    "resolution": resolution
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("hailuo_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_generation_task(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        model: str = "MiniMax-Hailuo-2.3",
        duration: int = 6,
        resolution: str = "768P",
        prompt_optimizer: bool = True
    ) -> str:
        """
        Create video generation task and return task_id.

        API Endpoint: POST /v1/video_generation
        """
        url = f"{self.BASE_URL}/v1/video_generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build payload
        payload = {
            "model": model,
            "prompt": prompt,
            "prompt_optimizer": prompt_optimizer,
            "duration": duration,
            "resolution": resolution
        }

        # Add first frame image if provided (Image-to-Video mode)
        if image_path:
            # Convert image to base64 data URL
            try:
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()

                # Detect image format
                from pathlib import Path
                ext = Path(image_path).suffix.lower()
                mime_type = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.webp': 'image/webp'
                }.get(ext, 'image/jpeg')

                # Create data URL
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                data_url = f"data:{mime_type};base64,{base64_image}"

                payload["first_frame_image"] = data_url

                logger.info("hailuo_image_encoded", mime_type=mime_type, size=len(image_bytes))
            except Exception as e:
                logger.error("hailuo_image_encode_failed", error=str(e))
                raise Exception(f"Failed to encode image: {e}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error("hailuo_api_error", status=response.status, error=error_text)
                    raise Exception(f"Hailuo API error {response.status}: {error_text}")

                data = await response.json()

                # Response format: {"task_id": "...", "base_resp": {"status_code": 0, "status_msg": "success"}}
                if data.get("base_resp", {}).get("status_code") != 0:
                    error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
                    raise Exception(f"Hailuo API error: {error_msg}")

                task_id = data.get("task_id")
                if not task_id:
                    raise Exception("No task_id in response")

                return task_id

    async def _poll_generation_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,  # 10 minutes
        poll_interval: int = 5  # 5 seconds
    ) -> str:
        """
        Poll generation status until complete.

        API Endpoint: GET /v1/query/video_generation?task_id={task_id}

        Returns:
            file_id of the generated video
        """
        url = f"{self.BASE_URL}/v1/query/video_generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if time.time() - start_time > max_wait_time:
                    raise Exception("Video generation timeout (10 minutes)")

                # Poll status
                async with session.get(url, headers=headers, params={"task_id": task_id}) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    data = await response.json()

                    # Check base_resp
                    if data.get("base_resp", {}).get("status_code") != 0:
                        error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
                        raise Exception(f"Status check error: {error_msg}")

                    # Get status
                    # Possible values: "Preparing", "Queueing", "Processing", "Success", "Fail"
                    status = data.get("status", "unknown")

                    # Update user if status changed
                    if status != last_status and progress_callback:
                        status_messages = {
                            "Preparing": "🔄 Подготовка к генерации...",
                            "Queueing": "⏳ Задача в очереди...",
                            "Processing": "⚙️ Генерирую видео..."
                        }
                        message = status_messages.get(status)
                        if message:
                            await progress_callback(message)

                    last_status = status

                    # Check if complete
                    if status == "Success":
                        file_id = data.get("file_id")
                        if not file_id:
                            raise Exception("file_id not found in success response")

                        logger.info("hailuo_generation_complete", file_id=file_id, task_id=task_id)
                        return file_id

                    # Check if failed
                    if status == "Fail":
                        error_code = data.get("base_resp", {}).get("status_code", "unknown")
                        error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
                        raise Exception(f"Generation failed (code {error_code}): {error_msg}")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)

    async def _download_video(self, file_id: str, filename: str) -> str:
        """
        Download video file from MiniMax API.

        API Endpoint: GET /v1/files/retrieve?file_id={file_id}

        Returns:
            Local path to downloaded video
        """
        url = f"{self.BASE_URL}/v1/files/retrieve"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            # First, get file info with download URL
            async with session.get(url, headers=headers, params={"file_id": file_id}) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"File retrieve failed: {response.status} - {error_text}")

                data = await response.json()

                # Check base_resp
                if data.get("base_resp", {}).get("status_code") != 0:
                    error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
                    raise Exception(f"File retrieve error: {error_msg}")

                # Get download URL
                file_info = data.get("file", {})
                download_url = file_info.get("download_url")

                if not download_url:
                    raise Exception("download_url not found in file info")

                logger.info("hailuo_download_url_received", url=download_url, file_id=file_id)

            # Now download the actual video file
            video_path = await self._download_file(download_url, filename)

            return video_path
