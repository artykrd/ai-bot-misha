"""
Kling AI video generation service.

Supports official Kling API with text-to-video, image-to-video, and multi-image-to-video.
"""
import time
import asyncio
import base64
import jwt
from typing import Optional, Callable, Awaitable, List
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import (
    get_kling_tokens_cost,
    get_kling_api_model,
    KLING_VERSION_TO_API,
)
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class KlingService(BaseVideoProvider):
    """
    Kling AI API integration for video generation.

    Supports text-to-video, image-to-video, and multi-image-to-video.
    Uses official Kling API with JWT authentication.
    """

    # Official Kling API
    OFFICIAL_API_URL = "https://api-singapore.klingai.com"
    # AI/ML API (alternative provider)
    AIML_API_URL = "https://api.aimlapi.com"

    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        use_official: bool = True
    ):
        """
        Initialize Kling service.

        Args:
            access_key: Kling API access key (for official API)
            secret_key: Kling API secret key (for official API)
            use_official: Whether to use official Kling API (True) or AI/ML API (False)
        """
        # For official API, we need access_key and secret_key
        self.access_key = access_key or getattr(settings, 'kling_access_key', None)
        self.secret_key = secret_key or getattr(settings, 'kling_secret_key', None)

        # For AI/ML API fallback
        self.aiml_api_key = getattr(settings, 'aimlapi_key', None)

        self.use_official = use_official and self.access_key and self.secret_key

        if self.use_official:
            self.base_url = self.OFFICIAL_API_URL
            logger.info("kling_using_official_api")
        else:
            self.base_url = self.AIML_API_URL
            logger.info("kling_using_aiml_api")

        # Initialize base class with a dummy key (we handle auth ourselves)
        super().__init__(self.access_key or self.aiml_api_key or "")

        self._jwt_token = None
        self._jwt_expires_at = 0

    def _generate_jwt_token(self) -> str:
        """
        Generate JWT token for official Kling API authentication.

        Token is valid for 30 minutes (1800 seconds).
        """
        if not self.access_key or not self.secret_key:
            raise ValueError("Kling access_key and secret_key are required for official API")

        current_time = int(time.time())

        # Check if existing token is still valid (with 5 minute buffer)
        if self._jwt_token and current_time < (self._jwt_expires_at - 300):
            return self._jwt_token

        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_key,
            "exp": current_time + 1800,  # 30 minutes
            "nbf": current_time - 5  # Start effective 5 seconds ago
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)

        self._jwt_token = token
        self._jwt_expires_at = current_time + 1800

        return token

    def _get_auth_headers(self) -> dict:
        """Get authentication headers for API requests."""
        headers = {
            "Content-Type": "application/json"
        }

        if self.use_official:
            token = self._generate_jwt_token()
            headers["Authorization"] = f"Bearer {token}"
        else:
            # AI/ML API uses simple Bearer token
            headers["Authorization"] = f"Bearer {self.aiml_api_key}"

        return headers

    async def _image_to_base64(self, image_path: str) -> str:
        """Convert local image file to base64 string."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(path, "rb") as f:
            image_data = f.read()

        # Return just the base64 string without data: prefix
        return base64.b64encode(image_data).decode("utf-8")

    async def generate_video(
        self,
        prompt: str,
        model: str = "kling-v2-5-turbo",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Kling AI.

        Args:
            prompt: Video generation prompt
            model: API model name (e.g., kling-v2-5-turbo, kling-v2-1-master, kling-v2-master)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - images: List of image paths (0-2 images)
                - duration: Video duration (5 or 10 seconds)
                - aspect_ratio: Aspect ratio (1:1, 16:9, 9:16)
                - version: UI version string for billing calculation

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        # Extract parameters
        images = kwargs.get("images", [])
        duration = kwargs.get("duration", 5)
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        version = kwargs.get("version", "2.5")  # UI version for billing

        # Calculate tokens for billing
        tokens_cost = get_kling_tokens_cost(version, duration)

        if not self.access_key and not self.aiml_api_key:
            return VideoResponse(
                success=False,
                error="Kling API credentials not configured",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Начинаю генерацию видео с Kling AI...")

            # Determine which endpoint to use based on number of images
            if len(images) == 0:
                # Text-to-video
                task_id = await self._create_text2video(
                    prompt=prompt,
                    model=model,
                    duration=duration,
                    aspect_ratio=aspect_ratio
                )
                endpoint_type = "text2video"
            elif len(images) == 1:
                # Image-to-video (single image)
                task_id = await self._create_image2video(
                    prompt=prompt,
                    model=model,
                    image_path=images[0],
                    duration=duration,
                    aspect_ratio=aspect_ratio
                )
                endpoint_type = "image2video"
            elif len(images) == 2:
                # Multi-image-to-video (start + end frame)
                # image_tail is NOT supported with kling-v2-5-turbo, force kling-v2-1-master
                multi_image_model = model
                if "turbo" in model or "v2-5" in model:
                    multi_image_model = "kling-v2-1-master"
                    logger.info(
                        "kling_model_override_for_image_tail",
                        original_model=model,
                        new_model=multi_image_model
                    )
                task_id = await self._create_multi_image2video(
                    prompt=prompt,
                    model=multi_image_model,
                    image_paths=images,
                    duration=duration,
                    aspect_ratio=aspect_ratio
                )
                endpoint_type = "image2video"  # Uses same polling endpoint
            else:
                return VideoResponse(
                    success=False,
                    error="Максимум 2 изображения поддерживаются",
                    processing_time=time.time() - start_time
                )

            logger.info(
                "kling_generation_created",
                task_id=task_id,
                model=model,
                endpoint=endpoint_type,
                images_count=len(images)
            )

            # Poll for video completion and get video_id
            video_url, video_id = await self._poll_generation_status(
                task_id=task_id,
                endpoint_type=endpoint_type,
                progress_callback=progress_callback
            )

            # Step 2: Add audio to video (video-to-audio)
            if self.use_official and video_id:
                if progress_callback:
                    await progress_callback("🔊 Генерирую звук для видео...")

                try:
                    audio_video_url = await self._add_audio_to_video(
                        video_id=video_id,
                        prompt=prompt,
                        progress_callback=progress_callback
                    )
                    # Use video with audio
                    video_url = audio_video_url
                    logger.info("kling_audio_added", video_id=video_id)
                except Exception as audio_error:
                    # If audio generation fails, continue with silent video
                    logger.warning(
                        "kling_audio_failed",
                        error=str(audio_error),
                        video_id=video_id
                    )
                    if progress_callback:
                        await progress_callback("⚠️ Звук не добавлен, продолжаю без аудио...")

            # Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "kling_video_generated",
                model=model,
                path=video_path,
                time=processing_time,
                tokens=tokens_cost
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                tokens_used=tokens_cost,
                metadata={
                    "provider": "kling",
                    "model": model,
                    "task_id": task_id,
                    "video_id": video_id,
                    "version": version,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "images_count": len(images)
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling_generation_failed", error=error_msg, model=model)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_text2video(
        self,
        prompt: str,
        model: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Create text-to-video generation task."""
        if self.use_official:
            url = f"{self.base_url}/v1/videos/text2video"
        else:
            url = f"{self.base_url}/generate/video/kling-ai/v1/generations"

        payload = {
            "model_name": model,
            "prompt": prompt,
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                await self._handle_response_errors(response)
                data = await response.json()

                if self.use_official:
                    return data.get("data", {}).get("task_id")
                else:
                    return data.get("id") or data.get("task_id")

    async def _create_image2video(
        self,
        prompt: str,
        model: str,
        image_path: str,
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Create image-to-video generation task."""
        if self.use_official:
            url = f"{self.base_url}/v1/videos/image2video"
        else:
            url = f"{self.base_url}/generate/video/kling-ai/v1/generations"

        # Convert image to base64
        image_base64 = await self._image_to_base64(image_path)

        payload = {
            "model_name": model,
            "prompt": prompt,
            "image": image_base64,
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                await self._handle_response_errors(response)
                data = await response.json()

                if self.use_official:
                    return data.get("data", {}).get("task_id")
                else:
                    return data.get("id") or data.get("task_id")

    async def _create_multi_image2video(
        self,
        prompt: str,
        model: str,
        image_paths: List[str],
        duration: int,
        aspect_ratio: str
    ) -> str:
        """Create multi-image-to-video generation task (start + end frame)."""
        if not self.use_official:
            raise ValueError("Multi-image-to-video requires official Kling API")

        url = f"{self.base_url}/v1/videos/image2video"

        # Convert images to base64
        image_base64 = await self._image_to_base64(image_paths[0])
        image_tail_base64 = await self._image_to_base64(image_paths[1]) if len(image_paths) > 1 else None

        payload = {
            "model_name": model,
            "prompt": prompt,
            "image": image_base64,
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
        }

        if image_tail_base64:
            payload["image_tail"] = image_tail_base64

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                await self._handle_response_errors(response)
                data = await response.json()
                return data.get("data", {}).get("task_id")

    async def _handle_response_errors(self, response: aiohttp.ClientResponse):
        """Handle API response errors with proper messages."""
        if response.status == 401:
            # Invalidate cached JWT token
            self._jwt_token = None
            self._jwt_expires_at = 0
            error_text = await response.text()
            raise Exception(f"Ошибка аутентификации. Проверьте ключи API. ({error_text})")

        if response.status == 429:
            error_text = await response.text()
            raise Exception(f"Превышен лимит запросов или недостаточно средств на аккаунте. ({error_text})")

        if response.status not in [200, 201]:
            error_text = await response.text()
            raise Exception(f"Kling API error: {response.status} - {error_text}")

    async def _poll_generation_status(
        self,
        task_id: str,
        endpoint_type: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,  # 10 minutes
        poll_interval: int = 5  # 5 seconds
    ) -> tuple:
        """
        Poll generation status until complete.

        Args:
            task_id: Task ID to poll
            endpoint_type: Type of endpoint (text2video or image2video)
            progress_callback: Optional callback for status updates
            max_wait_time: Maximum wait time in seconds
            poll_interval: Poll interval in seconds

        Returns:
            Tuple of (video_url, video_id)
        """
        if self.use_official:
            url = f"{self.base_url}/v1/videos/{endpoint_type}/{task_id}"
        else:
            url = f"{self.base_url}/generate/video/kling-ai/v1/generations/{task_id}"

        start_time = time.time()
        last_status = None
        retry_count = 0
        max_retries = 4

        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации видео (10 минут)")

                try:
                    async with session.get(
                        url,
                        headers=self._get_auth_headers()
                    ) as response:
                        if response.status == 401:
                            # Token expired, regenerate
                            self._jwt_token = None
                            self._jwt_expires_at = 0
                            await asyncio.sleep(poll_interval)
                            continue

                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Status check failed: {response.status} - {error_text}")

                        data = await response.json()

                        # Extract status based on API type
                        if self.use_official:
                            task_data = data.get("data", {})
                            status = task_data.get("task_status", "unknown")
                            status_msg = task_data.get("task_status_msg", "")
                        else:
                            status = data.get("status", "unknown")
                            status_msg = data.get("error", {}).get("message", "")

                        # Update user if status changed
                        if status != last_status and progress_callback:
                            if status in ["submitted", "pending", "queued"]:
                                await progress_callback("⏳ Видео в очереди...")
                            elif status in ["processing", "running"]:
                                await progress_callback("⚙️ Генерирую видео...")

                        last_status = status
                        retry_count = 0  # Reset retry count on successful response

                        # Check if complete
                        if status in ["succeed", "completed", "success", "succeeded"]:
                            # Get video URL and ID
                            if self.use_official:
                                videos = task_data.get("task_result", {}).get("videos", [])
                                if videos:
                                    video_url = videos[0].get("url")
                                    video_id = videos[0].get("id")
                                    return (video_url, video_id)
                            else:
                                video_url = (
                                    data.get("video_url") or
                                    data.get("url") or
                                    data.get("output", {}).get("video_url") or
                                    data.get("result", {}).get("video_url")
                                )
                                if video_url:
                                    return (video_url, None)

                            raise Exception("URL видео не найден в ответе")

                        # Check if failed
                        if status in ["failed", "error"]:
                            error_msg = status_msg or "Неизвестная ошибка"
                            raise Exception(f"Генерация не удалась: {error_msg}")

                except aiohttp.ClientError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Сетевая ошибка после {max_retries} попыток: {e}")
                    # Exponential backoff: 2s, 4s, 8s, 16s
                    backoff_time = 2 ** retry_count
                    logger.warning(
                        "kling_poll_retry",
                        retry=retry_count,
                        backoff=backoff_time,
                        error=str(e)
                    )
                    await asyncio.sleep(backoff_time)
                    continue

                # Wait before next poll
                await asyncio.sleep(poll_interval)

    async def _add_audio_to_video(
        self,
        video_id: str,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 300,  # 5 minutes for audio
        poll_interval: int = 5
    ) -> str:
        """
        Add AI-generated audio to video using video-to-audio API.

        Args:
            video_id: ID of the generated video
            prompt: Original prompt to help generate relevant audio
            progress_callback: Optional callback for status updates
            max_wait_time: Maximum wait time in seconds
            poll_interval: Poll interval in seconds

        Returns:
            URL of the video with audio
        """
        if not self.use_official:
            raise ValueError("Video-to-audio requires official Kling API")

        # Create video-to-audio task
        url = f"{self.base_url}/v1/audio/video-to-audio"

        payload = {
            "video_id": video_id,
            # Use prompt as sound effect hint (optional)
            # "sound_effect_prompt": prompt[:200] if prompt else None,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                await self._handle_response_errors(response)
                data = await response.json()
                audio_task_id = data.get("data", {}).get("task_id")

                if not audio_task_id:
                    raise Exception("Failed to create audio task")

                logger.info("kling_audio_task_created", task_id=audio_task_id)

        # Poll for audio completion
        poll_url = f"{self.base_url}/v1/audio/video-to-audio/{audio_task_id}"
        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации аудио")

                async with session.get(
                    poll_url,
                    headers=self._get_auth_headers()
                ) as response:
                    if response.status == 401:
                        self._jwt_token = None
                        self._jwt_expires_at = 0
                        await asyncio.sleep(poll_interval)
                        continue

                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Audio status check failed: {response.status} - {error_text}")

                    data = await response.json()
                    task_data = data.get("data", {})
                    status = task_data.get("task_status", "unknown")
                    status_msg = task_data.get("task_status_msg", "")

                    if status == "succeed":
                        # Get video with audio URL
                        videos = task_data.get("task_result", {}).get("videos", [])
                        if videos:
                            return videos[0].get("url")
                        raise Exception("URL видео со звуком не найден")

                    if status == "failed":
                        raise Exception(f"Генерация аудио не удалась: {status_msg}")

                await asyncio.sleep(poll_interval)

    # ======================
    # MOTION CONTROL
    # ======================

    async def generate_motion_control(
        self,
        image_path: str,
        video_url: str,
        mode: str = "std",
        character_orientation: str = "image",
        prompt: str = None,
        keep_original_sound: str = "yes",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
    ) -> VideoResponse:
        """
        Generate motion control video using Kling AI.

        Args:
            image_path: Path to reference image
            video_url: URL of the reference video
            mode: Generation mode ('std' or 'pro')
            character_orientation: Orientation of characters ('image' or 'video')
            prompt: Optional text prompt
            keep_original_sound: Whether to keep original sound ('yes' or 'no')
            progress_callback: Optional async callback for progress updates

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.use_official:
            return VideoResponse(
                success=False,
                error="Motion Control requires official Kling API",
                processing_time=time.time() - start_time
            )

        if not self.access_key:
            return VideoResponse(
                success=False,
                error="Kling API credentials not configured",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Создаю Motion Control видео...")

            # Create motion control task
            task_id = await self._create_motion_control_task(
                image_path=image_path,
                video_url=video_url,
                mode=mode,
                character_orientation=character_orientation,
                prompt=prompt,
                keep_original_sound=keep_original_sound,
            )

            logger.info("kling_motion_control_created", task_id=task_id)

            # Poll for completion
            video_result_url, video_id = await self._poll_motion_control_status(
                task_id=task_id,
                progress_callback=progress_callback
            )

            # Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path_result = await self._download_file(video_result_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "kling_motion_control_completed",
                path=video_path_result,
                time=processing_time
            )

            return VideoResponse(
                success=True,
                video_path=video_path_result,
                processing_time=processing_time,
                metadata={
                    "provider": "kling",
                    "type": "motion_control",
                    "task_id": task_id,
                    "video_id": video_id,
                    "mode": mode,
                    "character_orientation": character_orientation,
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("kling_motion_control_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_motion_control_task(
        self,
        image_path: str,
        video_url: str,
        mode: str = "std",
        character_orientation: str = "image",
        prompt: str = None,
        keep_original_sound: str = "yes",
    ) -> str:
        """Create motion control task via Kling API."""
        url = f"{self.base_url}/v1/videos/motion-control"

        # Convert image to base64
        image_base64 = await self._image_to_base64(image_path)

        payload = {
            "image_url": image_base64,
            "video_url": video_url,
            "mode": mode,
            "character_orientation": character_orientation,
            "keep_original_sound": keep_original_sound,
        }

        if prompt:
            payload["prompt"] = prompt[:2500]

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_auth_headers(),
                json=payload
            ) as response:
                await self._handle_response_errors(response)
                data = await response.json()
                task_id = data.get("data", {}).get("task_id")
                if not task_id:
                    raise Exception("Failed to create motion control task")
                return task_id

    async def _poll_motion_control_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,
        poll_interval: int = 5
    ) -> tuple:
        """Poll motion control task status."""
        url = f"{self.base_url}/v1/videos/motion-control/{task_id}"

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                if time.time() - start_time > max_wait_time:
                    raise Exception("Таймаут генерации Motion Control видео (10 минут)")

                async with session.get(
                    url,
                    headers=self._get_auth_headers()
                ) as response:
                    if response.status == 401:
                        self._jwt_token = None
                        self._jwt_expires_at = 0
                        await asyncio.sleep(poll_interval)
                        continue

                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    data = await response.json()
                    task_data = data.get("data", {})
                    status = task_data.get("task_status", "unknown")
                    status_msg = task_data.get("task_status_msg", "")

                    if status != last_status and progress_callback:
                        if status in ["submitted", "pending", "queued"]:
                            await progress_callback("⏳ Motion Control видео в очереди...")
                        elif status in ["processing", "running"]:
                            await progress_callback("⚙️ Генерирую Motion Control видео...")

                    last_status = status

                    if status in ["succeed", "completed", "success"]:
                        videos = task_data.get("task_result", {}).get("videos", [])
                        if videos:
                            video_url = videos[0].get("url")
                            video_id = videos[0].get("id")
                            return (video_url, video_id)
                        raise Exception("URL видео не найден в ответе")

                    if status in ["failed", "error"]:
                        error_msg = status_msg or "Неизвестная ошибка"
                        raise Exception(f"Motion Control не удался: {error_msg}")

                await asyncio.sleep(poll_interval)
