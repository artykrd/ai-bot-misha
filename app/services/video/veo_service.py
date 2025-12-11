"""
Google Veo 3.1 video generation service via Gemini API.
Updated for 2025 API - uses google-generativeai library.
"""
import time
import os
from typing import Optional, Callable, Awaitable
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.logger import get_logger
from app.services.video.base import BaseVideoProvider, VideoResponse

logger = get_logger(__name__)

# Lazy import - only import when actually used
_genai = None
_GENAI_CHECKED = False


def _get_genai():
    """Lazy import of google.genai."""
    global _genai, _GENAI_CHECKED

    if _GENAI_CHECKED:
        return _genai

    _GENAI_CHECKED = True
    try:
        from google import genai
        _genai = genai
        return _genai
    except Exception as e:
        logger.warning("genai_import_failed", error=str(e))
        _genai = None
        return None


class VeoService(BaseVideoProvider):
    """Google Veo 3.1 API integration via Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        # Veo 3.1 uses Gemini API key (not Vertex AI credentials)
        self.api_key = api_key or os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
        super().__init__(api_key=self.api_key or "")

        self.client = None
        self._genai = None

        # Don't import on init, wait until first use
        if self.api_key:
            self._genai = _get_genai()
            if self._genai:
                try:
                    # Initialize Gemini client with API key
                    # Set the API key as environment variable for the library
                    os.environ["GEMINI_API_KEY"] = self.api_key
                    self.client = self._genai.Client(api_key=self.api_key)
                    logger.info("veo_initialized", api_key_present=bool(self.api_key))
                except Exception as e:
                    logger.error("veo_init_failed", error=str(e))
                    self.client = None

    async def generate_video(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> VideoResponse:
        """
        Generate video using Google Veo 3.1.

        Args:
            prompt: Text description for video generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - duration: Video duration in seconds (4, 6, 8, default: 8)
                - aspect_ratio: Video aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, default: 16:9)
                - negative_prompt: Things to avoid in the video
                - resolution: Video resolution (720p, 1080p, default: 720p)
                - image_path: Path to first frame image for image-to-video (optional)
                - last_frame_path: Path to last frame image for interpolation (optional, requires image_path)
                - reference_images: List of up to 3 reference image paths (optional, Veo 3.1 only)
                - video_path: Path to Veo-generated video for extension (optional, Veo 3.1 only)

        Returns:
            VideoResponse with video path or error
        """
        start_time = time.time()

        if not self.client or not self.api_key:
            return VideoResponse(
                success=False,
                error="Google Gemini API key not configured. Set GOOGLE_GEMINI_API_KEY in .env. Get your key at: https://aistudio.google.com/apikey",
                processing_time=time.time() - start_time
            )

        try:
            if progress_callback:
                await progress_callback("🎬 Инициализация Veo 3.1...")

            if not self._genai:
                self._genai = _get_genai()

            if not self._genai:
                return VideoResponse(
                    success=False,
                    error="google-generativeai library not available. Install with: pip install google-generativeai>=0.8.3",
                    processing_time=time.time() - start_time
                )

            # Get parameters
            duration = kwargs.get("duration", 8)  # Default 8 seconds
            aspect_ratio = kwargs.get("aspect_ratio", "16:9")
            negative_prompt = kwargs.get("negative_prompt", None)
            resolution = kwargs.get("resolution", "720p")
            image_path = kwargs.get("image_path", None)
            last_frame_path = kwargs.get("last_frame_path", None)
            reference_images = kwargs.get("reference_images", None)
            input_video_path = kwargs.get("video_path", None)

            # Determine mode
            mode = "text-to-video"
            if input_video_path:
                mode = "video-extension"
            elif image_path and last_frame_path:
                mode = "interpolation"
            elif image_path:
                mode = "image-to-video"
            elif reference_images:
                mode = "reference-images"

            # Don't update progress here - keep the initial message from media_handler
            # The detailed progress message is already shown and should not be changed

            # Generate video using Veo model
            output_video_path = await self._generate_veo_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                negative_prompt=negative_prompt,
                resolution=resolution,
                image_path=image_path,
                last_frame_path=last_frame_path,
                reference_images=reference_images,
                input_video_path=input_video_path,
                progress_callback=progress_callback
            )

            processing_time = time.time() - start_time

            # Don't update progress here - the video result will be sent by media_handler
            # and the progress message will be deleted there

            logger.info(
                "veo_video_generated",
                prompt=prompt[:100],
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                mode=mode,
                time=processing_time
            )

            # Token usage for Veo 3.1: approximately 15,000 tokens per 8-second video
            tokens_used = 15000

            return VideoResponse(
                success=True,
                video_path=output_video_path,
                tokens_used=tokens_used,
                processing_time=processing_time,
                metadata={
                    "provider": "veo",
                    "model": "veo-3.1-generate-preview",
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "mode": mode,
                    "prompt": prompt
                }
            )

        except Exception as e:
            error_msg = str(e)

            # Special handling for quota/rate limit errors
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                error_msg = (
                    "❌ Превышена квота API или требуется платная подписка.\n\n"
                    "Veo 3.1 требует:\n"
                    "1. Активную оплату в Google AI Studio\n"
                    "2. Tier 1 или выше API ключ\n\n"
                    "Проверьте:\n"
                    "• https://aistudio.google.com/apikey (ваш API ключ)\n"
                    "• https://ai.dev/usage?tab=rate-limit (использование)\n"
                    "• https://ai.google.dev/pricing (цены и лимиты)\n\n"
                    f"Оригинальная ошибка: {error_msg}"
                )

            logger.error("veo_video_generation_failed", error=error_msg, prompt=prompt[:100])

            if progress_callback:
                await progress_callback(f"❌ Ошибка: см. сообщение ниже")

            return VideoResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time
            )

    async def _generate_veo_video(
        self,
        prompt: str,
        duration: int,
        aspect_ratio: str,
        negative_prompt: Optional[str],
        resolution: str,
        image_path: Optional[str] = None,
        last_frame_path: Optional[str] = None,
        reference_images: Optional[list] = None,
        input_video_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> str:
        """Generate video using Veo 3.1 model via Gemini API."""

        # Run in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()

        def _generate():
            try:
                # Prepare generation config according to official docs
                config_params = {}

                # Add aspect ratio
                if aspect_ratio:
                    config_params["aspect_ratio"] = aspect_ratio

                # Add negative prompt if provided
                if negative_prompt:
                    config_params["negative_prompt"] = negative_prompt

                # Add resolution if not default
                if resolution:
                    config_params["resolution"] = resolution

                # Add duration
                if duration:
                    config_params["duration_seconds"] = str(duration)

                # Prepare image parameter if provided
                # Need to create Part with Blob and call .as_image()
                image_obj = None
                if image_path:
                    try:
                        from google.genai import types
                        import mimetypes

                        # Read image file as bytes
                        with open(image_path, 'rb') as f:
                            image_bytes = f.read()

                        # Detect mime type
                        mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'

                        # Create Blob with raw bytes
                        blob = types.Blob(
                            mime_type=mime_type,
                            data=image_bytes  # raw bytes, not base64
                        )

                        # Create Part with inline_data
                        part = types.Part(inline_data=blob)

                        # Convert to Image using as_image() method
                        image_obj = part.as_image()

                        logger.info("veo_image_prepared",
                                  path=image_path,
                                  mime_type=mime_type,
                                  size=len(image_bytes))
                    except Exception as img_error:
                        logger.error("veo_image_prepare_failed", error=str(img_error))
                        raise Exception(f"Failed to prepare image: {img_error}")

                # Prepare reference images if provided (Veo 3.1 only)
                ref_images_objs = None
                if reference_images and len(reference_images) > 0:
                    try:
                        from google.genai import types
                        import mimetypes

                        ref_images_objs = []
                        for idx, ref_img_path in enumerate(reference_images[:3]):  # Max 3 images
                            # Read reference image as bytes
                            with open(ref_img_path, 'rb') as f:
                                ref_img_bytes = f.read()

                            ref_mime_type = mimetypes.guess_type(ref_img_path)[0] or 'image/jpeg'

                            # Create Blob and Part
                            ref_blob = types.Blob(
                                mime_type=ref_mime_type,
                                data=ref_img_bytes
                            )
                            ref_part = types.Part(inline_data=ref_blob)

                            # Convert to Image using as_image()
                            ref_image_obj = ref_part.as_image()

                            # Create VideoGenerationReferenceImage
                            ref_img = types.VideoGenerationReferenceImage(
                                image=ref_image_obj,
                                reference_type="asset"  # asset or style
                            )
                            ref_images_objs.append(ref_img)
                            logger.info("veo_reference_image_prepared",
                                      index=idx,
                                      path=ref_img_path,
                                      mime_type=ref_mime_type)

                        # Add reference images to config
                        config_params["reference_images"] = ref_images_objs
                    except Exception as ref_error:
                        logger.error("veo_reference_images_prepare_failed", error=str(ref_error))
                        raise Exception(f"Failed to prepare reference images: {ref_error}")

                # Prepare last frame for interpolation (Veo 3.1 only)
                # Requires both image_path and last_frame_path
                last_frame_obj = None
                if last_frame_path and image_path:
                    try:
                        from google.genai import types
                        import mimetypes

                        # Read last frame as bytes
                        with open(last_frame_path, 'rb') as f:
                            last_frame_bytes = f.read()

                        last_frame_mime = mimetypes.guess_type(last_frame_path)[0] or 'image/jpeg'

                        # Create Blob and Part
                        last_blob = types.Blob(
                            mime_type=last_frame_mime,
                            data=last_frame_bytes
                        )
                        last_part = types.Part(inline_data=last_blob)

                        # Convert to Image using as_image()
                        last_frame_obj = last_part.as_image()

                        # Add last_frame to config
                        config_params["last_frame"] = last_frame_obj

                        logger.info("veo_last_frame_prepared",
                                  path=last_frame_path,
                                  mime_type=last_frame_mime)
                    except Exception as last_error:
                        logger.error("veo_last_frame_prepare_failed", error=str(last_error))
                        raise Exception(f"Failed to prepare last frame: {last_error}")

                # Prepare video for extension (Veo 3.1 only)
                # Must be a video from a previous Veo generation
                video_obj = None
                if input_video_path:
                    try:
                        # For video extension, we need to upload the video file
                        # The video must be from a previous Veo generation
                        uploaded_video_file = self.client.files.upload(file=input_video_path)
                        video_obj = uploaded_video_file

                        logger.info("veo_input_video_uploaded", path=input_video_path, file_uri=uploaded_video_file.name)
                    except Exception as vid_error:
                        logger.error("veo_input_video_upload_failed", error=str(vid_error))
                        raise Exception(f"Failed to upload input video: {vid_error}")

                # Generate video using Veo 3.1 according to official Python example
                # from google import genai
                # client = genai.Client()
                # Different parameters depending on mode:
                # - Text-to-Video: prompt + config
                # - Image-to-Video: prompt + image + config
                # - Interpolation: prompt + image + config (with last_frame)
                # - Reference Images: prompt + config (with reference_images)
                # - Video Extension: prompt + video + config

                if video_obj:
                    # Video extension mode
                    operation = self.client.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=prompt,
                        video=video_obj,
                        config=config_params if config_params else None,
                    )
                else:
                    # All other modes (text, image, interpolation, reference)
                    operation = self.client.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=prompt,
                        image=image_obj if image_obj else None,
                        config=config_params if config_params else None,
                    )

                # Wait for the video to be generated (polling)
                # According to docs: poll until operation.done is True
                max_wait_time = 360  # 6 minutes max (docs say up to 6 min during peak)
                start = time.time()
                poll_interval = 10  # Poll every 10 seconds

                while not operation.done:
                    if time.time() - start > max_wait_time:
                        raise TimeoutError("Video generation timed out after 6 minutes")

                    time.sleep(poll_interval)
                    # Refresh operation status
                    operation = self.client.operations.get(operation)

                # Check if operation completed with error
                if hasattr(operation, 'error') and operation.error:
                    error_msg = str(operation.error)
                    logger.error("veo_operation_error", error=error_msg)
                    raise Exception(f"Video generation failed: {error_msg}")

                # Get the generated video from response
                # According to docs: operation.response.generated_videos[0]
                if not operation.response:
                    logger.error("veo_no_response", operation_name=operation.name if hasattr(operation, 'name') else 'unknown')
                    raise Exception("Video generation completed but no response received. The operation may have failed.")

                # Log response structure for debugging
                logger.info("veo_response_received",
                          has_response=bool(operation.response),
                          response_type=type(operation.response).__name__,
                          response_attrs=dir(operation.response) if operation.response else [])

                # Try to access generated_videos
                if not hasattr(operation.response, 'generated_videos'):
                    logger.error("veo_no_generated_videos_attr",
                               response_attrs=dir(operation.response))
                    raise Exception("Response doesn't have 'generated_videos' attribute. Check API response structure.")

                if not operation.response.generated_videos:
                    # Check if content was filtered by Google's Responsible AI filters
                    if hasattr(operation.response, 'rai_media_filtered_count'):
                        filter_count = getattr(operation.response, 'rai_media_filtered_count', 0)
                        filter_reasons = getattr(operation.response, 'rai_media_filtered_reasons', [])

                        if filter_count and filter_count > 0:
                            logger.error("veo_content_filtered",
                                       filtered_count=filter_count,
                                       filter_reasons=filter_reasons)

                            # Provide user-friendly error message
                            error_msg = (
                                "❌ Видео было заблокировано фильтрами безопасности Google.\n\n"
                                "Возможные причины:\n"
                                "• Запрос содержит реалистичные изображения людей\n"
                                "• Контент нарушает политику использования Google AI\n"
                                "• Промпт содержит запрещенные темы\n\n"
                                "Попробуйте:\n"
                                "• Изменить промпт на менее конкретный\n"
                                "• Использовать мультяшный/анимационный стиль вместо реалистичного\n"
                                "• Убрать упоминания реалистичных людей или животных\n"
                                "• Использовать другие изображения"
                            )
                            raise Exception(error_msg)

                    # If not filtered, check other attributes
                    video_attrs = [attr for attr in dir(operation.response) if 'video' in attr.lower()]
                    logger.error("veo_generated_videos_empty",
                               video_related_attrs=video_attrs,
                               all_attrs=[attr for attr in dir(operation.response) if not attr.startswith('_')])
                    raise Exception("generated_videos list is empty. Video may still be processing or generation failed.")

                generated_video = operation.response.generated_videos[0]

                # Save video to storage
                filename = self._generate_filename("mp4")
                video_path = self.storage_path / filename

                # Download and save video file
                # According to docs: client.files.download(file=video.video)
                self.client.files.download(file=generated_video.video)
                generated_video.video.save(str(video_path))

                logger.info(
                    "veo_video_saved",
                    path=str(video_path),
                    size=video_path.stat().st_size
                )

                return str(video_path)

            except Exception as e:
                logger.error("veo_generation_error", error=str(e))
                raise

        try:
            # Don't override the initial progress message from media_handler
            # The improved message is already shown there

            # Generate video in executor to not block async event loop
            video_path = await loop.run_in_executor(None, _generate)

            return video_path

        except Exception as e:
            logger.error("veo_executor_error", error=str(e))
            raise
