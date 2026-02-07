"""
Sora 2 video generation service via Kie.ai API.
Callback-based architecture: createTask with callBackUrl, no polling.
Supports: Stable (text/image-to-video), Pro (text/image-to-video), Characters Pro.
"""
from typing import Optional

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

CALLBACK_URL = "https://mikhail-bot.archy-tech.ru/api/sora_callback"

# Model name mapping for API calls
SORA_MODELS = {
    "sora2-stable-t2v": "sora-2-text-to-video-stable",
    "sora2-stable-i2v": "sora-2-image-to-video-stable",
    "sora2-pro-t2v": "sora-2-text-to-video",
    "sora2-pro-i2v": "sora-2-image-to-video",
    "sora2-characters-pro": "sora-2-characters-pro",
}


class SoraService(BaseVideoProvider):
    """Sora 2 API integration via Kie.ai.

    Uses callback-based flow:
    1. createTask with callBackUrl → returns taskId
    2. Kie.ai sends result to callBackUrl when done
    3. No polling needed

    Supports 5 models:
    - sora-2-text-to-video-stable (Stable text-to-video)
    - sora-2-image-to-video-stable (Stable image-to-video)
    - sora-2-text-to-video (Pro text-to-video)
    - sora-2-image-to-video (Pro image-to-video)
    - sora-2-characters-pro (Characters Pro)
    """

    BASE_URL = "https://api.kie.ai"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'kie_api_key', None) or "")
        if not self.api_key:
            logger.warning("kie_api_key_missing")

    async def generate_video(
        self,
        prompt: str,
        model: str = "sora-2-text-to-video-stable",
        progress_callback=None,
        **kwargs
    ) -> VideoResponse:
        """Legacy sync interface — not used in callback flow.
        Kept for compatibility with VideoJobService.process_job().
        """
        raise NotImplementedError(
            "SoraService uses callback-based flow. "
            "Use create_task() + callback endpoint instead."
        )

    async def create_task(
        self,
        prompt: str,
        model: str = "sora-2-text-to-video-stable",
        **kwargs
    ) -> str:
        """
        Create video generation task with callback URL.
        Returns taskId immediately without waiting for result.

        Args:
            prompt: Video generation prompt
            model: API model name
            **kwargs: Additional parameters:
                - aspect_ratio: 'portrait' or 'landscape' (default: 'landscape')
                - n_frames: '10' or '15' (duration in seconds, default: '10')
                - image_url: URL of image for image-to-video models
                - remove_watermark: bool (only for Pro models)

        Returns:
            taskId string from Kie.ai API

        Raises:
            Exception: If API returns error or no taskId
        """
        if not self.api_key:
            raise Exception("Kie.ai API ключ не настроен. Добавьте KIE_API_KEY в .env файл.")

        payload = self._build_payload(model, prompt, **kwargs)
        payload["callBackUrl"] = CALLBACK_URL

        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()

                if data.get("code") != 200:
                    error_msg = data.get("message", "Unknown error")
                    raise Exception(f"Kie.ai API error: {error_msg}")

                task_id = data.get("data", {}).get("taskId")
                if not task_id:
                    raise Exception("No taskId in API response")

                logger.info(
                    "sora_task_created",
                    task_id=task_id,
                    model=model,
                    callback_url=CALLBACK_URL,
                )

                return task_id

    def _build_payload(self, model: str, prompt: str, **kwargs) -> dict:
        """Build API request payload based on model type."""
        payload = {
            "model": model,
            "input": {}
        }

        if model == "sora-2-characters-pro":
            payload["input"]["character_prompt"] = prompt
            if kwargs.get("origin_task_id"):
                payload["input"]["origin_task_id"] = kwargs["origin_task_id"]
            if kwargs.get("character_user_name"):
                payload["input"]["character_user_name"] = kwargs["character_user_name"]
            if kwargs.get("timestamps"):
                payload["input"]["timestamps"] = kwargs["timestamps"]
            if kwargs.get("safety_instruction"):
                payload["input"]["safety_instruction"] = kwargs["safety_instruction"]
        else:
            payload["input"]["prompt"] = prompt
            payload["input"]["aspect_ratio"] = kwargs.get("aspect_ratio", "landscape")
            payload["input"]["n_frames"] = kwargs.get("n_frames", "10")
            payload["input"]["upload_method"] = "s3"

            if "image" in model and kwargs.get("image_url"):
                payload["input"]["image_urls"] = [kwargs["image_url"]]

            if model in ("sora-2-text-to-video", "sora-2-image-to-video"):
                payload["input"]["remove_watermark"] = kwargs.get("remove_watermark", True)

        return payload
