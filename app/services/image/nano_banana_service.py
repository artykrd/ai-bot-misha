"""
Nano Banana - Image generation service via Kie.ai API.
Supports Nano Banana (google/nano-banana) and Nano Banana PRO (nano-banana-pro).
"""
import time
import asyncio
import json
from typing import Optional, Callable, Awaitable, List
from pathlib import Path

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger
from app.core.billing_config import get_image_model_billing
from app.services.image.base import BaseImageProvider, ImageResponse

logger = get_logger(__name__)


class NanoBananaService(BaseImageProvider):
    """
    Nano Banana image generation via Kie.ai API.

    Supports two models:
    - google/nano-banana (basic) - text-to-image
    - nano-banana-pro (PRO) - text-to-image and image-to-image (up to 8 images)

    Two-step async flow:
    1. POST /api/v1/jobs/createTask -> returns taskId
    2. Poll GET /api/v1/jobs/recordInfo?taskId=... until state=success
    """

    BASE_URL = "https://api.kie.ai"
    UPLOAD_BASE_URL = "https://kieai.redpandaai.co"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or getattr(settings, 'kie_api_key', None) or "")
        if not self.api_key:
            logger.warning("kie_api_key_missing_for_nano_banana")

    def _get_auth_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    async def process_image(
        self,
        image_path: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """Process image (redirects to generate_image with the image as input)."""
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return ImageResponse(
                success=False,
                error="Prompt is required for image editing"
            )
        return await self.generate_image(
            prompt=prompt,
            progress_callback=progress_callback,
            reference_image_path=image_path,
            **{k: v for k, v in kwargs.items() if k != "prompt"}
        )

    async def generate_image(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> ImageResponse:
        """
        Generate image using Nano Banana via Kie.ai API.

        Args:
            prompt: Text description for image generation
            progress_callback: Optional async callback for progress updates
            **kwargs: Additional parameters:
                - model: Internal model key (gemini-2.5-flash-image or gemini-3-pro-image-preview)
                - aspect_ratio: Image aspect ratio (default: 1:1)
                - number_of_images: Number of images (for billing metadata, default: 1)
                - reference_image_path: Path to reference image (optional)
                - image_urls: List of image URLs for upload (optional)

        Returns:
            ImageResponse with image path or error
        """
        start_time = time.time()

        if not self.api_key:
            return ImageResponse(
                success=False,
                error="Kie.ai API key not configured. Set KIE_API_KEY in .env",
                processing_time=time.time() - start_time
            )

        # Parse parameters - keep same interface as before
        model_key = kwargs.get("model", "gemini-2.5-flash-image")
        is_pro = "3-pro" in model_key
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        number_of_images = kwargs.get("number_of_images", 1)
        reference_image_path = kwargs.get("reference_image_path")
        image_urls = kwargs.get("image_urls", [])

        has_images = bool(reference_image_path or image_urls)

        # Auto-upgrade to PRO when images are provided,
        # because google/nano-banana doesn't support image_input
        actual_is_pro = is_pro
        if has_images and not actual_is_pro:
            actual_is_pro = True
            logger.info("nano_banana_auto_upgrade_to_pro", reason="image_input_requires_pro")

        mode = "image-to-image" if has_images else "text-to-image"
        model_display = "Nano Banana PRO" if actual_is_pro else "Nano Banana"

        try:
            if progress_callback:
                await progress_callback(
                    f"🎨 Генерирую изображение ({model_display}, {mode}, {aspect_ratio})..."
                )

            # Build API payload
            if actual_is_pro:
                kie_model = "nano-banana-pro"
                payload = {
                    "model": kie_model,
                    "input": {
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "resolution": "1K",
                        "output_format": "png",
                    }
                }
            else:
                kie_model = "google/nano-banana"
                payload = {
                    "model": kie_model,
                    "input": {
                        "prompt": prompt,
                        "output_format": "png",
                        "image_size": aspect_ratio,
                    }
                }

            # Upload and attach images for PRO model
            if actual_is_pro and has_images:
                uploaded_urls = []

                # Upload from URLs first (e.g. Telegram file URLs)
                if image_urls:
                    for img_url in image_urls[:8]:
                        try:
                            kie_url = await self._upload_url_to_kie(img_url)
                            uploaded_urls.append(kie_url)
                        except Exception as e:
                            logger.warning("nano_banana_url_upload_failed", url=img_url[:100], error=str(e))

                # Fall back to local file upload
                if not uploaded_urls and reference_image_path:
                    try:
                        kie_url = await self._upload_image_to_kie(reference_image_path)
                        uploaded_urls.append(kie_url)
                    except Exception as e:
                        logger.warning("nano_banana_image_upload_failed", path=reference_image_path, error=str(e))

                if uploaded_urls:
                    payload["input"]["image_input"] = uploaded_urls

            # Log payload
            log_payload = {
                "model": payload.get("model"),
                "input": {
                    k: v for k, v in payload.get("input", {}).items()
                    if k != "image_input"
                },
                "has_images": "image_input" in payload.get("input", {}),
                "images_count": len(payload.get("input", {}).get("image_input", [])),
            }
            logger.info("nano_banana_create_task_payload", payload=log_payload)

            # Step 1: Create task
            task_id = await self._create_task(payload)

            logger.info(
                "nano_banana_task_created",
                task_id=task_id,
                model=kie_model,
                mode=mode,
                aspect_ratio=aspect_ratio,
            )

            if progress_callback:
                await progress_callback("⏳ Изображение генерируется...")

            # Step 2: Poll for result
            image_url = await self._poll_task_status(task_id, progress_callback)

            # Step 3: Download image
            if progress_callback:
                await progress_callback("📥 Скачиваю изображение...")

            filename = self._generate_filename("png")
            image_path_result = await self._download_file(image_url, filename)

            processing_time = time.time() - start_time

            if progress_callback:
                await progress_callback("✅ Изображение готово!")

            logger.info(
                "nano_banana_image_generated",
                path=image_path_result,
                time=processing_time,
                model=kie_model,
                mode=mode,
            )

            # Billing based on original model selection (not auto-upgraded)
            billing_id = "banana-pro" if is_pro else "nano-banana-image"
            nano_billing = get_image_model_billing(billing_id)
            tokens_used = nano_billing.tokens_per_generation * number_of_images

            return ImageResponse(
                success=True,
                image_path=image_path_result,
                processing_time=processing_time,
                metadata={
                    "provider": "nano_banana",
                    "model": kie_model,
                    "aspect_ratio": aspect_ratio,
                    "mode": mode,
                    "prompt": prompt,
                    "tokens_used": tokens_used,
                    "task_id": task_id,
                },
            )

        except Exception as e:
            error_msg = str(e)

            # Downgrade user-caused errors to warning
            is_user_error = any(p in error_msg for p in [
                "Prohibited Use policy", "filtered out", "502:", "503 Service",
                "unexpected mimetype", "Bad gateway", "безопасности",
            ])
            if is_user_error:
                logger.warning(
                    "nano_banana_generation_user_error",
                    error=error_msg,
                    prompt=prompt[:100] if prompt else "None",
                )
            else:
                logger.error(
                    "nano_banana_generation_failed",
                    error=error_msg,
                    prompt=prompt[:100] if prompt else "None",
                )

            # User-friendly error messages
            if "429" in error_msg or "Превышен лимит" in error_msg:
                error_msg = (
                    "❌ Сервис временно перегружен (превышена квота API).\n\n"
                    "Мы уже пробовали несколько раз — пожалуйста, повторите запрос\n"
                    "через 2-3 минуты. Приносим извинения за ожидание!"
                )
            elif "Prohibited Use policy" in error_msg or "filtered out" in error_msg:
                error_msg = (
                    "🛡️ Генерация заблокирована фильтром безопасности.\n"
                    "Попробуйте изменить промпт или использовать другое изображение."
                )
            elif "502" in error_msg or "Bad gateway" in error_msg or "503" in error_msg:
                error_msg = (
                    "⚠️ Сервис временно недоступен (ошибка сервера).\n"
                    "Попробуйте повторить запрос через несколько минут."
                )
            elif "unexpected mimetype" in error_msg or "text/html" in error_msg:
                error_msg = (
                    "⚠️ Сервис временно недоступен.\n"
                    "Попробуйте повторить запрос через несколько минут."
                )

            if progress_callback:
                await progress_callback("❌ Ошибка генерации")

            return ImageResponse(
                success=False,
                error=error_msg,
                processing_time=time.time() - start_time,
            )

    # ------------------------------------------------------------------
    # KIE API helpers (same pattern as NanoBanana2Service)
    # ------------------------------------------------------------------

    async def _upload_image_to_kie(self, image_path: str) -> str:
        """Upload local image file to Kie.ai and return the file URL."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        url = f"{self.UPLOAD_BASE_URL}/api/file-stream-upload"
        timeout = aiohttp.ClientTimeout(total=60)

        file_bytes = path.read_bytes()

        async with aiohttp.ClientSession(timeout=timeout) as session:
            data = aiohttp.FormData()
            data.add_field(
                'file',
                file_bytes,
                filename=path.name,
                content_type='image/jpeg',
            )
            data.add_field('uploadPath', 'nano-banana')

            async with session.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=data,
            ) as response:
                response_text = await response.text()

                if response.status != 200:
                    raise Exception(
                        f"File upload HTTP {response.status}: {response_text[:300]}"
                    )

                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    raise Exception(f"File upload invalid JSON: {response_text[:300]}")

                if result.get("code") != 200:
                    raise Exception(
                        f"File upload error: {result.get('msg', 'Unknown')}"
                    )

                resp_data = result.get("data", {})
                file_url = resp_data.get("downloadUrl") or resp_data.get("fileUrl")
                if not file_url:
                    raise Exception(
                        f"No downloadUrl in upload response: {response_text[:300]}"
                    )

                logger.info(
                    "nano_banana_image_uploaded",
                    path=image_path,
                    url=file_url,
                )

                return file_url

    async def _upload_url_to_kie(self, file_url: str) -> str:
        """Upload a remote file URL to Kie.ai and return the hosted URL."""
        url = f"{self.UPLOAD_BASE_URL}/api/file-url-upload"
        timeout = aiohttp.ClientTimeout(total=60)

        payload = {
            "fileUrl": file_url,
            "uploadPath": "nano-banana",
        }

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            ) as response:
                response_text = await response.text()

                if response.status != 200:
                    raise Exception(
                        f"URL upload HTTP {response.status}: {response_text[:300]}"
                    )

                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    raise Exception(f"URL upload invalid JSON: {response_text[:300]}")

                if result.get("code") != 200:
                    raise Exception(
                        f"URL upload error: {result.get('msg', 'Unknown')}"
                    )

                resp_data = result.get("data", {})
                hosted_url = resp_data.get("downloadUrl") or resp_data.get("fileUrl")
                if not hosted_url:
                    raise Exception("No downloadUrl in URL upload response")

                logger.info("nano_banana_url_uploaded", source=file_url[:80], hosted=hosted_url)
                return hosted_url

    async def _create_task(self, payload: dict) -> str:
        """Create a generation task via Kie.ai API with retry for transient errors."""
        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
        timeout = aiohttp.ClientTimeout(total=60)
        max_retries = 3

        for attempt in range(max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        url,
                        headers=self._get_auth_headers(),
                        json=payload,
                    ) as response:
                        response_status = response.status
                        response_text = await response.text()

                        logger.info(
                            "nano_banana_api_response",
                            status=response_status,
                            response_body=response_text[:1000],
                            url=url,
                            attempt=attempt,
                        )

                        # Retry on 5xx server errors
                        if response_status >= 500 and attempt < max_retries:
                            backoff = 2 ** (attempt + 1)
                            logger.warning(
                                "nano_banana_server_error_retry",
                                status=response_status,
                                attempt=attempt + 1,
                                backoff=backoff,
                            )
                            await asyncio.sleep(backoff)
                            continue

                        if response_status != 200:
                            raise Exception(
                                f"Kie.ai API HTTP {response_status}: {response_text[:500]}"
                            )

                        try:
                            data = json.loads(response_text)
                        except json.JSONDecodeError as e:
                            raise Exception(
                                f"Kie.ai API вернул невалидный JSON: {response_text[:300]}. Error: {e}"
                            )

                        if data.get("code") != 200:
                            error_msg = data.get("msg") or data.get("message") or "Unknown error"
                            error_code = data.get("code", "unknown")

                            logger.error(
                                "nano_banana_api_error",
                                error_code=error_code,
                                error_msg=error_msg,
                                full_response=response_text[:500],
                            )

                            if error_code == 401:
                                raise Exception("Ошибка аутентификации. Проверьте KIE_API_KEY.")
                            elif error_code == 402:
                                raise Exception("Недостаточно средств на аккаунте Kie.ai.")
                            elif error_code == 429:
                                raise Exception("Превышен лимит запросов. Попробуйте позже.")
                            elif error_code == 422:
                                raise Exception(f"Ошибка валидации параметров: {error_msg}")
                            else:
                                raise Exception(f"Kie.ai API error ({error_code}): {error_msg}")

                        task_id = data.get("data", {}).get("taskId")
                        if not task_id:
                            raise Exception(f"No taskId in API response: {response_text[:300]}")

                        return task_id

            except aiohttp.ClientError as e:
                if attempt < max_retries:
                    backoff = 2 ** (attempt + 1)
                    logger.warning(
                        "nano_banana_network_error_retry",
                        error=str(e),
                        attempt=attempt + 1,
                        backoff=backoff,
                    )
                    await asyncio.sleep(backoff)
                    continue
                raise Exception(f"Kie.ai API network error after {max_retries} retries: {e}")

    async def _poll_task_status(
        self,
        task_id: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        max_wait_time: int = 600,
        poll_interval: int = 5,
    ) -> str:
        """
        Poll task status until completion.

        Args:
            task_id: Task ID from createTask response
            progress_callback: Optional progress callback
            max_wait_time: Maximum wait time in seconds (default 10 minutes)
            poll_interval: Polling interval in seconds

        Returns:
            Image URL from resultJson
        """
        url = f"{self.BASE_URL}/api/v1/jobs/recordInfo"
        start_time = time.time()
        last_state = None
        retry_count = 0
        max_retries = 4

        async with aiohttp.ClientSession() as session:
            while True:
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    raise Exception("Таймаут генерации изображения (10 минут)")

                try:
                    async with session.get(
                        url,
                        headers=self._get_auth_headers(),
                        params={"taskId": task_id},
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(f"Status check failed: {response.status} - {error_text}")

                        data = await response.json()

                        if data.get("code") != 200:
                            error_msg = data.get("msg", "Unknown error")
                            raise Exception(f"Status API error: {error_msg}")

                        task_data = data.get("data", {})
                        state = task_data.get("state", "unknown")

                        # Update progress on state change
                        if state != last_state and progress_callback:
                            elapsed_int = int(elapsed)
                            state_messages = {
                                "waiting": f"⏳ В очереди... ({elapsed_int}с)",
                                "queuing": f"⏳ В очереди на генерацию... ({elapsed_int}с)",
                                "generating": f"🎨 Генерирую изображение... ({elapsed_int}с)",
                            }
                            msg = state_messages.get(state)
                            if msg:
                                await progress_callback(msg)

                        last_state = state
                        retry_count = 0

                        if state == "success":
                            # Extract image URL from resultJson
                            result_json_str = task_data.get("resultJson", "{}")
                            try:
                                result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
                            except json.JSONDecodeError:
                                raise Exception("Ошибка разбора результата генерации")

                            result_urls = result_json.get("resultUrls", [])
                            if not result_urls:
                                raise Exception("URL изображения не найден в ответе")

                            return result_urls[0]

                        if state == "fail":
                            fail_msg = task_data.get("failMsg") or "Неизвестная ошибка"
                            fail_code = task_data.get("failCode") or ""
                            raise Exception(f"Генерация не удалась: {fail_msg} ({fail_code})")

                except aiohttp.ClientError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Сетевая ошибка после {max_retries} попыток: {e}")
                    backoff_time = 2 ** retry_count
                    logger.warning(
                        "nano_banana_poll_retry",
                        retry=retry_count,
                        backoff=backoff_time,
                        error=str(e),
                    )
                    await asyncio.sleep(backoff_time)
                    continue

                await asyncio.sleep(poll_interval)
