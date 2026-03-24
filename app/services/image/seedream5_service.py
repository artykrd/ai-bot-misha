"""
Seedream 5.0 Lite AI image generation service (ByteDance).
Documentation: https://docs.byteplus.com/en/docs/ModelArk/1666945

Model:
- seedream-5-0-260128 (Seedream 5.0 Lite) - Latest model with best prompt understanding

Features:
- Text-to-Image generation
- Image-to-Image transformation (single or multiple reference images)
- Batch image generation (up to 15 images)
- Multiple resolution options (2K, 3K, custom sizes)
- Output format selection (jpeg, png)
- Prompt optimization
- Streaming support
- Watermark control

Uses customized inference endpoint for API calls.
"""
import time
import base64
from typing import Optional, Callable, Awaitable, List

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


# Model ID
SEEDREAM5_MODEL = "seedream-5-0-260128"

# Available sizes for Seedream 5.0 Lite
# Seedream 5.0 supports 2K and 3K resolutions (no 4K)
SEEDREAM5_SIZES = {
    # 2K resolution
    "2K|1:1": "2048x2048",
    "2K|4:3": "2304x1728",
    "2K|3:4": "1728x2304",
    "2K|16:9": "2848x1600",
    "2K|9:16": "1600x2848",
    "2K|3:2": "2496x1664",
    "2K|2:3": "1664x2496",
    "2K|21:9": "3136x1344",
    # 3K resolution
    "3K|1:1": "3072x3072",
    "3K|4:3": "3456x2592",
    "3K|3:4": "2592x3456",
    "3K|16:9": "4096x2304",
    "3K|9:16": "2304x4096",
    "3K|3:2": "3744x2496",
    "3K|2:3": "2496x3744",
    "3K|21:9": "4704x2016",
}

# Default size when using resolution-only mode (model picks aspect ratio)
SEEDREAM5_RESOLUTION_SIZES = {
    "2K": "2K",
    "3K": "3K",
}


class Seedream5Service(BaseImageProvider):
    """
    Seedream 5.0 Lite API integration for image generation.

    Supports:
    - Text-to-Image: Generate images from text prompts
    - Image-to-Image: Transform images using text prompts
    - Multi-Image Blending: Combine multiple reference images
    - Batch Generation: Generate up to 15 related images
    - Output Format: JPEG or PNG
    - Prompt Optimization: Standard mode

    Pricing (in tokens):
    - Seedream 5.0: 25,000 tokens per image

    Uses customized inference endpoint (not preset endpoint).
    """

    BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'ark_api_key', None))
        self.endpoint_id = endpoint_id or getattr(settings, 'seedream_5_endpoint_id', None)
        if not self.api_key:
            logger.warning("ark_api_key_missing", message="ARK_API_KEY not configured")
        if not self.endpoint_id:
            logger.warning("seedream5_endpoint_id_missing", message="SEEDREAM_5_ENDPOINT_ID not configured")

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Seedream 5.0 Lite.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - size: Image size key (e.g. "2K|1:1", "3K|16:9", "2K", "3K")
                - reference_image: Optional reference image path or URL
                - reference_images: Optional list of reference images
                - watermark: Add watermark (default: False)
                - batch_mode: Enable batch generation (default: False)
                - max_images: Max images for batch mode (1-15, default: 1)
                - optimize_prompt: "standard" or None (default: None)
                - output_format: "jpeg" or "png" (default: "jpeg")

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
                error="Seedream 5.0 endpoint не настроен. Добавьте SEEDREAM_5_ENDPOINT_ID в .env файл.",
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
            output_format = kwargs.get("output_format", "jpeg")

            model_id = self.endpoint_id
            billing_key = "seedream-5.0"

            # Resolve size
            resolved_size = self._resolve_size(size)

            if progress_callback:
                mode_text = "по фото" if reference_image or reference_images else "по тексту"
                await progress_callback(f"✨ Генерирую изображение {mode_text} с Seedream 5.0 Lite...")

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
                optimize_prompt=optimize_prompt,
                output_format=output_format
            )

            if progress_callback:
                await progress_callback("💾 Сохраняю изображение...")

            # Download and save images
            file_ext = "png" if output_format == "png" else "jpg"
            saved_images = []
            for idx, image_info in enumerate(result.get("data", [])):
                if "url" in image_info:
                    filename = self._generate_filename(file_ext)
                    image_path = await self._download_file(image_info["url"], filename)
                    saved_images.append({
                        "path": image_path,
                        "size": image_info.get("size", resolved_size)
                    })
                elif "b64_json" in image_info:
                    filename = self._generate_filename(file_ext)
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
                "seedream5_image_generated",
                model=model_id,
                size=resolved_size,
                images_count=len(saved_images),
                has_reference=bool(images_data),
                output_format=output_format,
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
                    "provider": "seedream5",
                    "model": model_id,
                    "model_version": "5.0",
                    "size": resolved_size,
                    "prompt": prompt,
                    "images_count": len(saved_images),
                    "all_images": saved_images,
                    "has_reference": bool(images_data),
                    "tokens_used": total_tokens,
                    "tokens_per_image": tokens_per_image,
                    "output_format": output_format,
                    "usage": result.get("usage", {})
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("seedream5_generation_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    def _resolve_size(self, size: str) -> str:
        """Resolve size key to actual pixel dimensions or resolution keyword."""
        # Check if it's a combined key like "2K|1:1"
        if size in SEEDREAM5_SIZES:
            return SEEDREAM5_SIZES[size]
        # Check if it's just a resolution keyword
        if size in SEEDREAM5_RESOLUTION_SIZES:
            return SEEDREAM5_RESOLUTION_SIZES[size]
        # Fallback - return as-is (might be a direct pixel value)
        return size

    async def _prepare_image(self, image_source: str) -> Optional[str]:
        """Prepare image for API (convert to base64 or return URL)."""
        try:
            if image_source.startswith(('http://', 'https://')):
                return image_source

            from pathlib import Path
            path = Path(image_source)
            if path.exists():
                with open(path, 'rb') as f:
                    image_data = f.read()

                if path.suffix.lower() in ['.jpg', '.jpeg']:
                    mime_type = 'jpeg'
                elif path.suffix.lower() == '.png':
                    mime_type = 'png'
                elif path.suffix.lower() == '.webp':
                    mime_type = 'webp'
                elif path.suffix.lower() == '.bmp':
                    mime_type = 'bmp'
                elif path.suffix.lower() == '.tiff':
                    mime_type = 'tiff'
                else:
                    mime_type = 'jpeg'

                b64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/{mime_type};base64,{b64_data}"

            return None

        except Exception as e:
            logger.error("seedream5_image_prepare_failed", error=str(e), source=image_source)
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
        optimize_prompt: Optional[str] = None,
        output_format: str = "jpeg"
    ) -> dict:
        """
        Call Seedream 5.0 API to generate image.

        API Endpoint: POST /api/v3/images/generations
        """
        url = f"{self.BASE_URL}/images/generations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": "url",
            "watermark": watermark,
            "output_format": output_format
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

        # Prompt optimization (Seedream 5.0 supports only "standard" mode)
        if optimize_prompt:
            payload["optimize_prompt_options"] = {
                "mode": optimize_prompt
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    logger.error("seedream5_api_error", status=response.status, error=error_text)

                    try:
                        import json
                        error_data = json.loads(error_text)
                        error_code = error_data.get("error", {}).get("code", "")
                        error_message = error_data.get("error", {}).get("message", error_text)
                    except Exception:
                        error_code = ""
                        error_message = error_text

                    if response.status == 404 or "NotFound" in error_code:
                        raise Exception(
                            f"Модель {model} недоступна. Проверьте, что модель активирована в вашем аккаунте BytePlus."
                        )
                    elif "SensitiveContent" in error_code:
                        raise Exception(
                            "Изображение содержит запрещённый контент. Попробуйте изменить промпт."
                        )
                    else:
                        raise Exception(f"Seedream 5.0 API error {response.status}: {error_message}")

                data = await response.json()

                if "data" not in data or len(data["data"]) == 0:
                    if "error" in data:
                        raise Exception(f"API Error: {data['error'].get('message', 'Unknown error')}")
                    raise Exception("No image data in response")

                logger.info(
                    "seedream5_api_response",
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
        """Process/transform existing image using Seedream 5.0."""
        prompt = kwargs.get("prompt", "Enhance this image")

        return await self.generate_image(
            prompt=prompt,
            progress_callback=progress_callback,
            reference_image=image_path,
            **kwargs
        )

    @staticmethod
    def get_available_sizes() -> dict:
        """Get available sizes for Seedream 5.0 Lite."""
        return SEEDREAM5_SIZES

    @staticmethod
    def get_model_info() -> dict:
        """Get model information including capabilities and pricing."""
        return {
            "id": SEEDREAM5_MODEL,
            "name": "Seedream 5.0 Lite",
            "description": "Умная модель — лучше понимает замысел по короткому описанию",
            "capabilities": [
                "Генерация по тексту",
                "Генерация по фото + текст",
                "Редактирование фото + текст",
                "Смешивание нескольких фото (2-14)",
                "Пакетная генерация (до 15 изображений)",
                "Разрешение 2K и 3K",
                "Выбор формата: JPEG / PNG",
                "Оптимизация промпта"
            ],
            "tokens_per_image": 25000,
            "max_reference_images": 14,
            "max_batch_images": 15,
            "resolutions": ["2K", "3K"],
            "aspect_ratios": ["1:1", "4:3", "3:4", "16:9", "9:16"],
            "output_formats": ["jpeg", "png"]
        }
