"""
Google Gemini image generation and processing service.
Uses Imagen 3 for generation and Gemini Vision for analysis.
"""
import time
from typing import Optional, Callable, Awaitable
from pathlib import Path
import asyncio
import os

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)

# Lazy import - only import when actually used
_vertexai = None
_genai = None
_GEMINI_CHECKED = False


def _get_gemini_libs():
    """Lazy import of google libraries."""
    global _vertexai, _genai, _GEMINI_CHECKED

    if _GEMINI_CHECKED:
        return (_vertexai, _genai)

    _GEMINI_CHECKED = True
    try:
        # Try Vertex AI first (for Imagen)
        try:
            import vertexai
            from vertexai.preview.vision_models import ImageGenerationModel
            _vertexai = {
                'vertexai': vertexai,
                'ImageGenerationModel': ImageGenerationModel
            }
        except Exception as e:
            logger.warning("vertexai_import_failed", error=str(e))
            _vertexai = None

        # Try Google AI (for Gemini Vision)
        try:
            import google.generativeai as genai
            _genai = genai
        except Exception as e:
            logger.warning("google_generativeai_import_failed", error=str(e))
            _genai = None

        return (_vertexai, _genai)
    except Exception as e:
        logger.warning("gemini_libs_import_failed", error=str(e))
        return (None, None)


class GeminiImageService(BaseImageProvider):
    """
    Google Gemini/Imagen integration for image generation and processing.

    - Uses Imagen 3 (via Vertex AI) for image generation
    - Uses Gemini Vision for image analysis and understanding
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        location: str = "us-central1"
    ):
        super().__init__(api_key or settings.google_ai_api_key)

        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.vertexai_client = None
        self.genai_client = None

        # Initialize libraries
        self._vertexai, self._genai = _get_gemini_libs()

        # Initialize Vertex AI (for Imagen)
        if self._vertexai and self.project_id:
            try:
                self._vertexai['vertexai'].init(
                    project=self.project_id,
                    location=self.location
                )
                self.vertexai_client = True
                logger.info(
                    "imagen_initialized",
                    project=self.project_id,
                    location=self.location
                )
            except Exception as e:
                logger.error("imagen_init_failed", error=str(e))
                self.vertexai_client = None

        # Initialize Google AI (for Gemini Vision)
        if self._genai and self.api_key:
            try:
                self._genai.configure(api_key=self.api_key)
                self.genai_client = True
                logger.info("gemini_vision_initialized")
            except Exception as e:
                logger.error("gemini_vision_init_failed", error=str(e))
                self.genai_client = None

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Imagen 3.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 3:4, 4:3, default: 1:1)
                - negative_prompt: Things to avoid in the image
                - number_of_images: Number of images to generate (1-4, default: 1)
                - safety_filter_level: Safety filter (block_most, block_some, block_few)

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.vertexai_client or not self.project_id:
            return ImageResponse(
                success=False,
                error="Google Cloud project not configured or Vertex AI not initialized",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎨 Инициализация Imagen 3...")

            # Get parameters
            aspect_ratio = kwargs.get("aspect_ratio", "1:1")
            negative_prompt = kwargs.get("negative_prompt", None)
            number_of_images = kwargs.get("number_of_images", 1)
            safety_filter = kwargs.get("safety_filter_level", "block_some")

            if progress_callback:
                await progress_callback(f"🖼 Генерирую изображение ({aspect_ratio})...")

            # Generate image using Imagen
            image_path = await self._generate_imagen(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt,
                number_of_images=number_of_images,
                safety_filter=safety_filter,
                progress_callback=progress_callback
            )

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "imagen_generated",
                prompt=prompt[:100],
                aspect_ratio=aspect_ratio,
                time=processing_time
            )

            gemini_billing = get_image_model_billing("nano-banana-image")
            tokens_used = gemini_billing.tokens_per_generation

            return ImageResponse(
                success=True,
                image_path=image_path,
                processing_time=processing_time,
                metadata={
                    "provider": "google",
                    "model": "imagen-3",
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt,
                    "tokens_used": tokens_used
                }
            )

        except Exception as e:
            error_msg = str(e)
            logger.error("imagen_generation_failed", error=error_msg, prompt=prompt[:100])

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def analyze_image(
        self,
        image_path: str,
        prompt: str = "Опиши это изображение подробно",
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> dict:
        """
        Analyze image using Gemini Vision.

        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters

        Returns:
            Dict with analysis results
        """
        start_time = time.time()

        if not self.genai_client:
            return {
                "success": False,
                "error": "Gemini Vision not configured",
                "processing_time": time.time() - start_time
            }

        try:
            input_file = Path(image_path)
            if not input_file.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            if progress_callback:
                await progress_callback("🔍 Анализирую изображение...")

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()

            def _analyze():
                # Load image
                import PIL.Image
                img = PIL.Image.open(image_path)

                # Create Gemini model
                model = self._genai.GenerativeModel('gemini-2.0-flash-exp')

                # Generate analysis
                response = model.generate_content([prompt, img])
                return response.text

            analysis = await loop.run_in_executor(None, _analyze)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Анализ завершен!")

            logger.info(
                "gemini_vision_analyzed",
                image=image_path,
                time=processing_time
            )

            return {
                "success": True,
                "analysis": analysis,
                "processing_time": processing_time,
                "tokens_used": 1000
            }

        except Exception as e:
            error_msg = str(e)
            logger.error("gemini_vision_failed", error=error_msg)

            if progress_callback:
                await progress_callback(f"❌ Ошибка: {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "processing_time": time.time() - start_time
            }

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Process image using Gemini Vision.

        Args:
            image_path: Path to input image
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters

        Returns:
            ImageResponse with analysis or error
        """
        operation = kwargs.get("operation", "analyze")

        if operation == "analyze":
            result = await self.analyze_image(
                image_path,
                kwargs.get("prompt", "Опиши это изображение подробно"),
                progress_callback,
                **kwargs
            )

            if result["success"]:
                return ImageResponse(
                    success=True,
                    image_path=image_path,
                    processing_time=result["processing_time"],
                    metadata={
                        "provider": "google",
                        "operation": "analyze",
                        "analysis": result["analysis"],
                        "tokens_used": result.get("tokens_used", 1000)
                    }
                )
            else:
                return ImageResponse(
                    success=False,
                    error=result["error"],
                    processing_time=result["processing_time"]
                )
        else:
            return ImageResponse(
                success=False,
                error=f"Unsupported operation: {operation}"
            )

    async def _generate_imagen(
        self,
        prompt: str,
        aspect_ratio: str,
        negative_prompt: Optional[str],
        number_of_images: int,
        safety_filter: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate image using Imagen model."""

        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # Load the Imagen model
                model = self._vertexai['ImageGenerationModel'].from_pretrained("imagen-3.0-generate-001")

                # Generate image
                response = model.generate_images(
                    prompt=prompt,
                    number_of_images=number_of_images,
                    aspect_ratio=aspect_ratio,
                    negative_prompt=negative_prompt,
                    safety_filter_level=safety_filter,
                )

                # Get the first image from response
                image = response.images[0]

                # Save image to storage
                filename = self._generate_filename("png")
                image_path = self.storage_path / filename

                # Save image
                image.save(location=str(image_path))

                logger.info(
                    "imagen_saved",
                    path=str(image_path),
                    size=image_path.stat().st_size
                )

                return str(image_path)

            except Exception as e:
                logger.error("imagen_generation_error", error=str(e))
                raise

        try:
            if progress_callback:
                await progress_callback("⏳ Обработка запроса...")

            # Generate image in executor
            image_path = await loop.run_in_executor(None, _generate)

            return image_path

        except Exception as e:
            logger.error("imagen_executor_error", error=str(e))
            raise
