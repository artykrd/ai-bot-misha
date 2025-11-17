"""
Replicate video generation service for Hailuo, Kling, and other models.
"""
import time
import asyncio
from typing import Optional, Callable, Awaitable, Dict, Any

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)


class ReplicateService(BaseVideoProvider):
    """Replicate API integration for video generation (Hailuo, Kling, etc.)."""

    BASE_URL = "https://api.replicate.com/v1"

    # Model mappings
    MODELS = {
        "hailuo": "minimax/video-01",
        "kling": "kling-ai/kling-v1",
        "kling_effects": "kling-ai/kling-v1-effects"
    }

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or settings.replicate_api_key)
        if not self.api_key:
            logger.warning("replicate_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        model: str = "hailuo",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Replicate models.

        Args:
            prompt: Video generation prompt
            model: Model name (hailuo, kling, kling_effects)
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters specific to the model

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.api_key:
            return VideoResponse(
                success=False,
                error="Replicate API key not configured",
                processing_time=time.time() - start_time
            )

        if model not in self.MODELS:
            return VideoResponse(
                success=False,
                error=f"Unknown model: {model}. Available: {', '.join(self.MODELS.keys())}",
                processing_time=time.time() - start_time
            )

        try:
            model_name = self._get_model_display_name(model)

            # Notify user that generation is starting
            if progress_callback:
                await progress_callback(f"🎬 Начинаю генерацию видео с {model_name}...")

            # Step 1: Create prediction
            prediction_id = await self._create_prediction(prompt, model, **kwargs)
            logger.info(
                "replicate_prediction_created",
                prediction_id=prediction_id,
                model=model
            )

            # Step 2: Poll for completion
            video_url = await self._poll_prediction_status(
                prediction_id,
                progress_callback
            )

            # Step 3: Download video
            if progress_callback:
                await progress_callback("📥 Скачиваю видео...")

            filename = self._generate_filename("mp4")
            video_path = await self._download_file(video_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Видео готово!")

            logger.info(
                "replicate_video_generated",
                model=model,
                path=video_path,
                time=processing_time
            )

            return VideoResponse(
                success=True,
                video_path=video_path,
                processing_time=processing_time,
                metadata={
                    "provider": "replicate",
                    "model": model,
                    "prediction_id": prediction_id
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("replicate_generation_failed", error=error_msg, model=model)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _create_prediction(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> str:
        """Create prediction request and return prediction ID."""
        url = f"{self.BASE_URL}/predictions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        model_version = self.MODELS[model]

        # Build input parameters based on model
        input_params = self._build_model_input(prompt, model, **kwargs)

        payload = {
            "version": model_version,
            "input": input_params
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Replicate API error: {response.status} - {error_text}")

                data = await response.json()
                return data["id"]

    def _build_model_input(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Build input parameters specific to each model."""
        input_params = {"prompt": prompt}

        if model == "hailuo":
            # Hailuo/MiniMax specific parameters
            if "duration" in kwargs:
                input_params["duration"] = kwargs["duration"]
            if "aspect_ratio" in kwargs:
                input_params["aspect_ratio"] = kwargs["aspect_ratio"]

        elif model in ["kling", "kling_effects"]:
            # Kling specific parameters
            if "duration" in kwargs:
                input_params["duration"] = kwargs["duration"]
            if "aspect_ratio" in kwargs:
                input_params["aspect_ratio"] = kwargs["aspect_ratio"]
            if "creativity" in kwargs:
                input_params["creativity"] = kwargs["creativity"]

            # Kling effects specific
            if model == "kling_effects" and "effect_type" in kwargs:
                input_params["effect_type"] = kwargs["effect_type"]

        return input_params

    async def _poll_prediction_status(
        self,
        prediction_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 900,  # 15 minutes
        poll_interval: int = 5  # 5 seconds
    ) -> str:
        """
        Poll prediction status until complete.

        Returns:
            URL of the generated video
        """
        url = f"{self.BASE_URL}/predictions/{prediction_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        start_time = time.time()
        last_status = None

        async with aiohttp.ClientSession() as session:
            while True:
                # Check timeout
                if time.time() - start_time > max_wait_time:
                    raise Exception("Video generation timeout")

                # Poll status
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Status check failed: {response.status} - {error_text}")

                    data = await response.json()
                    status = data.get("status", "unknown")

                    # Update user if status changed
                    if status != last_status and progress_callback:
                        if status == "starting":
                            await progress_callback("🚀 Запускаю модель...")
                        elif status == "processing":
                            await progress_callback("⚙️ Генерирую видео...")

                    last_status = status

                    # Check if complete
                    if status == "succeeded":
                        # Get video URL from output
                        output = data.get("output")
                        if isinstance(output, list) and len(output) > 0:
                            video_url = output[0]
                        elif isinstance(output, str):
                            video_url = output
                        else:
                            raise Exception("Video URL not found in prediction output")

                        return video_url

                    # Check if failed
                    if status == "failed":
                        error = data.get("error", "Unknown error")
                        raise Exception(f"Generation failed: {error}")

                    # Check if canceled
                    if status == "canceled":
                        raise Exception("Generation was canceled")

                    # Wait before next poll
                    await asyncio.sleep(poll_interval)

    def _get_model_display_name(self, model: str) -> str:
        """Get user-friendly model name."""
        names = {
            "hailuo": "Hailuo (MiniMax)",
            "kling": "Kling AI",
            "kling_effects": "Kling Effects"
        }
        return names.get(model, model)
