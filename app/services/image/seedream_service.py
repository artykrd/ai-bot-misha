"""
Seedream AI image generation service (ByteDance).
Documentation: https://docs.byteplus.com/en/docs/ModelArk/1666945

Model:
- seedream-4-5-251128 (Seedream 4.5) - Latest version with best quality

Features:
- Text-to-Image generation
- Image-to-Image transformation (single or multiple reference images)
- Batch image generation (up to 15 images)
- Multiple resolution options (2K, 4K, custom sizes)
- Streaming support
- Watermark control

Uses customized inference endpoint for API calls.
"""
import time
import base64
from typing import Optional, Callable, Awaitable, List, Union
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


# Model ID
# Note: Model IDs have format: seedream-{version}-{release_date}
# Check https://console.byteplus.com/ark/openManagement for available models
SEEDREAM_MODEL = "seedream-4-5-251128"

# Available sizes for Seedream 4.5
# Format: "{resolution}|{aspect_ratio}" -> pixel dimensions
SEEDREAM_SIZES = {
    # 2K resolution
    "2K|auto": "2K",
    "2K|1:1": "2048x2048",
    "2K|4:3": "2304x1728",
    "2K|3:4": "1728x2304",
    "2K|16:9": "2560x1440",
    "2K|9:16": "1440x2560",
    "2K|3:2": "2496x1664",
    "2K|2:3": "1664x2496",
    "2K|21:9": "3024x1296",
    # 4K resolution
    "4K|auto": "4K",
    "4K|1:1": "4096x4096",
    "4K|4:3": "4608x3456",
    "4K|3:4": "3456x4608",
    "4K|16:9": "5120x2880",
    "4K|9:16": "2880x5120",
    "4K|3:2": "4992x3328",
    "4K|2:3": "3328x4992",
    "4K|21:9": "6048x2592",
    # Backward compatibility (legacy single-key format)
    "2K": "2K",
    "4K": "4K",
    "1:1": "2048x2048",
    "4:3": "2304x1728",
    "3:4": "1728x2304",
    "16:9": "2560x1440",
    "9:16": "1440x2560",
    "3:2": "2496x1664",
    "2:3": "1664x2496",
    "21:9": "3024x1296",
}


class SeedreamService(BaseImageProvider):
    """
    Seedream AI API integration for image generation.

    Supports:
    - Text-to-Image: Generate images from text prompts
    - Image-to-Image: Transform images using text prompts
    - Multi-Image Blending: Combine multiple reference images
    - Batch Generation: Generate up to 15 related images

    Pricing (in tokens):
    - Seedream 4.5: 19,300 tokens per image

    Uses customized inference endpoint (not preset endpoint).
    """

    BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'ark_api_key', None))
        self.endpoint_id = endpoint_id or getattr(settings, 'seedream_endpoint_id', None)
        if not self.api_key:
            logger.warning("ark_api_key_missing", message="ARK_API_KEY not configured")
        if not self.endpoint_id:
            logger.warning("seedream_endpoint_id_missing", message="SEEDREAM_ENDPOINT_ID not configured")

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Seedream AI.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - size: Image size (default: "2K")
                - reference_image: Optional reference image path or URL
                - reference_images: Optional list of reference images
                - watermark: Add watermark (default: False)
                - batch_mode: Enable batch generation (default: False)
                - max_images: Max images for batch mode (1-15, default: 1)
                - optimize_prompt: "standard" or "fast" (default: None - disabled)

        Returns:
            ImageResponse with image path(s) or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="ARK API ключ не настроен. Добавьте ARK_API_KEY в .env файл.",
                processing_time=time.time() - start_time
            )

        if not self.endpoint_id:
            return ImageResponse(
                success=False,
                error="Seedream endpoint не настроен. Добавьте SEEDREAM_ENDPOINT_ID в .env файл.",
                processing_time=time.time() - start_time
            )

        try:
            # Get parameters
            size = kwargs.get("size", "2K")
            reference_image = kwargs.get("reference_image")
            reference_images = kwargs.get("reference_images", [])
            watermark = kwargs.get("watermark", False)
            batch_mode = kwargs.get("batch_mode", False)
            max_images = kwargs.get("max_images", 1)
            optimize_prompt = kwargs.get("optimize_prompt")

            # Use Seedream 4.5 model
            # When using customized endpoint, model should be the endpoint_id
            model_id = self.endpoint_id
            billing_key = "seedream-4.5"

            # Resolve size
            resolved_size = SEEDREAM_SIZES.get(size, size)

            if progress_callback:
                mode_text = "по фото" if reference_image or reference_images else "по тексту"
                await progress_callback(f"🎨 Генерирую изображение {mode_text} с Seedream 4.5...")

            # Prepare reference images
            images_data = []
            if reference_image:
                image_data = await self._prepare_image(reference_image)
                if image_data:
                    images_data.append(image_data)

            if reference_images:
                for img in reference_images:
                    image_data = await self._prepare_image(img)
                    if image_data:
                        images_data.append(image_data)

            # Generate image(s)
            result = await self._generate_image_api(
                prompt=prompt,
                model=model_id,
                size=resolved_size,
                images=images_data if images_data else None,
                watermark=watermark,
                batch_mode=batch_mode,
                max_images=max_images,
                optimize_prompt=optimize_prompt
            )

            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

            # Download and save images
            saved_images = []
            for idx, image_info in enumerate(result.get("data", [])):
                if "url" in image_info:
                    filename = self._generate_filename("jpg")
                    image_path = await self._download_file(image_info["url"], filename)
                    saved_images.append({
                        "path": image_path,
                        "size": image_info.get("size", resolved_size)
                    })
                elif "b64_json" in image_info:
                    filename = self._generate_filename("jpg")
                    image_path = self.storage_path / filename
                    image_bytes = base64.b64decode(image_info["b64_json"])
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    saved_images.append({
                        "path": str(image_path),
                        "size": image_info.get("size", resolved_size)
                    })

            if not saved_images:
                raise Exception("Не удалось сохранить изображения")

            processing_time = time.time() - start_time

            if progress_callback:
                if len(saved_images) > 1:
                    await progress_callback(f"✅ Сгенерировано {len(saved_images)} изображений!")
                else:
                    await progress_callback("✅ Изображение готово!")

            logger.info(
                "seedream_image_generated",
                model=model_id,
                size=resolved_size,
                images_count=len(saved_images),
                has_reference=bool(images_data),
                prompt=prompt[:100],
                time=processing_time
            )

            # Get billing info
            billing = get_image_model_billing(billing_key)
            tokens_per_image = billing.tokens_per_generation
            total_tokens = tokens_per_image * len(saved_images)

            return ImageResponse(
                success=True,
                image_path=saved_images[0]["path"],
                processing_time=processing_time,
                metadata={
                    "provider": "seedream",
                    "model": model_id,
                    "model_version": "4.5",
                    "size": resolved_size,
                    "prompt": prompt,
                    "images_count": len(saved_images),
                    "all_images": saved_images,
                    "has_reference": bool(images_data),
                    "tokens_used": total_tokens,
                    "tokens_per_image": tokens_per_image,
                    "usage": result.get("usage", {})
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("seedream_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _prepare_image(self, image_source: str) -> Optional[str]:
        """
        Prepare image for API (convert to base64 or return URL).

        Args:
            image_source: File path or URL

        Returns:
            Base64 encoded image string or URL
        """
        try:
            if image_source.startswith(('http://', 'https://')):
                return image_source

            # Local file - convert to base64
            path = Path(image_source)
            if path.exists():
                with open(path, 'rb') as f:
                    image_data = f.read()

                # Detect image format
                if path.suffix.lower() in ['.jpg', '.jpeg']:
                    mime_type = 'jpeg'
                elif path.suffix.lower() == '.png':
                    mime_type = 'png'
                elif path.suffix.lower() == '.webp':
                    mime_type = 'webp'
                else:
                    mime_type = 'jpeg'

                b64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/{mime_type};base64,{b64_data}"

            return None

        except Exception as e:
            logger.error("seedream_image_prepare_failed", error=str(e), source=image_source)
            return None

    async def _generate_image_api(
        self,
        prompt: str,
        model: str,
        size: str = "2K",
        images: Optional[List[str]] = None,
        watermark: bool = False,
        batch_mode: bool = False,
        max_images: int = 1,
        optimize_prompt: Optional[str] = None
    ) -> dict:
        """
        Call Seedream API to generate image.

        API Endpoint: POST /api/v3/images/generations
        Uses endpoint_id in model field for customized inference.

        Returns:
            API response with image data
        """
        # Standard images endpoint - endpoint_id is passed in model field
        url = f"{self.BASE_URL}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build payload
        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": "url",
            "watermark": watermark
        }

        # Add reference image(s)
        if images:
            if len(images) == 1:
                payload["image"] = images[0]
            else:
                payload["image"] = images

        # Batch generation settings
        if batch_mode:
            payload["sequential_image_generation"] = "auto"
            payload["sequential_image_generation_options"] = {
                "max_images": min(max_images, 15)
            }
        else:
            payload["sequential_image_generation"] = "disabled"

        # Prompt optimization
        if optimize_prompt:
            payload["optimize_prompt_options"] = {
                "mode": optimize_prompt
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error("seedream_api_error", status=response.status, error=error_text)

                    # Parse error message
                    try:
                        import json
                        error_data = json.loads(error_text)
                        error_code = error_data.get("error", {}).get("code", "")
                        error_message = error_data.get("error", {}).get("message", error_text)
                    except:
                        error_code = ""
                        error_message = error_text

                    # Handle specific error codes
                    if response.status == 404 or "NotFound" in error_code:
                        raise Exception(
                            f"Модель {model} недоступна. Проверьте, что модель активирована в вашем аккаунте BytePlus."
                        )
                    elif "SensitiveContent" in error_code:
                        raise Exception(
                            "Изображение содержит запрещённый контент. Попробуйте изменить промпт."
                        )
                    else:
                        raise Exception(f"Seedream API error {response.status}: {error_message}")

                data = await response.json()

                if "data" not in data or len(data["data"]) == 0:
                    # Check for error in response
                    if "error" in data:
                        raise Exception(f"API Error: {data['error'].get('message', 'Unknown error')}")
                    raise Exception("No image data in response")

                logger.info(
                    "seedream_api_response",
                    images_count=len(data.get("data", [])),
                    usage=data.get("usage", {})
                )

                return data

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process/transform existing image using Seedream.

        Args:
            image_path: Path to the source image
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters including 'prompt' for transformation

        Returns:
            ImageResponse with processed image or error
        """
        prompt = kwargs.get("prompt", "Enhance this image")

        return await self.generate_image(
            prompt=prompt,
            progress_callback=progress_callback,
            reference_image=image_path,
            **kwargs
        )

    @staticmethod
    def get_available_sizes() -> dict:
        """Get available sizes for Seedream 4.5."""
        return SEEDREAM_SIZES

    @staticmethod
    def get_model_info() -> dict:
        """Get model information including capabilities and pricing."""
        return {
            "id": SEEDREAM_MODEL,
            "name": "Seedream 4.5",
            "description": "Последняя версия с лучшим качеством генерации",
            "capabilities": [
                "Генерация по тексту",
                "Генерация по фото + текст",
                "Смешивание нескольких фото (2-14)",
                "Пакетная генерация (до 15 изображений)",
                "Разрешение 2K и 4K"
            ],
            "tokens_per_image": 19300,
            "max_reference_images": 14,
            "max_batch_images": 15,
            "sizes": list(SEEDREAM_SIZES.keys())
        }
