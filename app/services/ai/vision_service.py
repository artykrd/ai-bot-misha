"""
OpenAI GPT-4 Vision service for image analysis.
"""
import time
import base64
from pathlib import Path
from typing import Optional, List, Dict

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.services.ai.base import AIResponse

logger = get_logger(__name__)


class VisionService:
    """OpenAI GPT-4 Vision for image analysis."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def analyze_image(
        self,
        image_path: str,
        prompt: str = "Проанализируй это изображение подробно.",
        model: str = "gpt-4o",
        max_tokens: int = 500,
        detail: str = "auto",
        **kwargs
    ) -> AIResponse:
        """
        Analyze image using GPT-4 Vision.

        Args:
            image_path: Path to image file
            prompt: Question or instruction about the image
            model: Vision model (gpt-4o, gpt-4-turbo, gpt-4.1)
            max_tokens: Maximum tokens in response
            detail: Image detail level ('low', 'high', 'auto')
            **kwargs: Additional parameters

        Returns:
            AIResponse with analysis text
        """
        start_time = time.time()

        if not self.api_key:
            return AIResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        try:
            # Encode image to base64
            image_data = self._encode_image(image_path)

            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ]

            # Call API
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                **kwargs
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            processing_time = time.time() - start_time

            logger.info(
                "vision_image_analyzed",
                model=model,
                tokens=tokens_used,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=content,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={
                    "model": model,
                    "detail": detail,
                    "image_path": image_path
                }
            )

        except Exception as e:
            logger.error("vision_analysis_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    async def analyze_multiple_images(
        self,
        image_paths: List[str],
        prompt: str = "Проанализируй эти изображения.",
        model: str = "gpt-4o",
        max_tokens: int = 1000,
        detail: str = "auto",
        **kwargs
    ) -> AIResponse:
        """
        Analyze multiple images (up to 10) using GPT-4 Vision.

        Args:
            image_paths: List of paths to image files (max 10)
            prompt: Question or instruction about the images
            model: Vision model
            max_tokens: Maximum tokens in response
            detail: Image detail level
            **kwargs: Additional parameters

        Returns:
            AIResponse with analysis text
        """
        start_time = time.time()

        if not self.api_key:
            return AIResponse(
                success=False,
                error="OpenAI API key not configured",
                processing_time=time.time() - start_time
            )

        if len(image_paths) > 10:
            return AIResponse(
                success=False,
                error="Maximum 10 images allowed per request",
                processing_time=time.time() - start_time
            )

        try:
            # Prepare content with text and all images
            content = [{"type": "text", "text": prompt}]

            for image_path in image_paths:
                image_data = self._encode_image(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}",
                        "detail": detail
                    }
                })

            # Prepare messages
            messages = [{"role": "user", "content": content}]

            # Call API
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                **kwargs
            )

            result_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            processing_time = time.time() - start_time

            logger.info(
                "vision_multiple_images_analyzed",
                model=model,
                images_count=len(image_paths),
                tokens=tokens_used,
                time=processing_time
            )

            return AIResponse(
                success=True,
                content=result_content,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={
                    "model": model,
                    "detail": detail,
                    "images_count": len(image_paths)
                }
            )

        except Exception as e:
            logger.error("vision_multiple_analysis_failed", error=str(e))
            return AIResponse(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
