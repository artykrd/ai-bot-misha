"""
Helper for uploading binary files to the Kie.ai file host.

Returns a public ``downloadUrl`` that third-party services (e.g. the official
Kling API) can fetch directly. This is required because Telegram file URLs
(``api.telegram.org/file/bot<token>/...``) are NOT reliably fetchable by
external providers — Kling Motion Control fails them with error 1201
("couldn't get the contents of the file").

The same host (``kieai.redpandaai.co/api/file-stream-upload``) is already used
for Nano Banana image uploads, so Kling is known to fetch these URLs fine.
"""
import json

import aiohttp

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

UPLOAD_BASE_URL = "https://kieai.redpandaai.co"


async def upload_bytes_to_kie(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    upload_path: str = "uploads",
    timeout_seconds: int = 120,
) -> str:
    """
    Upload raw bytes to the Kie.ai file host and return a public URL.

    Args:
        file_bytes: File contents.
        filename: Original filename (used by the host for the stored object).
        content_type: MIME type, e.g. ``video/mp4``.
        upload_path: Logical folder on the host.
        timeout_seconds: Total request timeout.

    Returns:
        Public download URL of the uploaded file.

    Raises:
        ValueError: if KIE_API_KEY is not configured.
        Exception: on HTTP / parsing errors.
    """
    api_key = getattr(settings, "kie_api_key", None)
    if not api_key:
        raise ValueError("KIE_API_KEY is not configured")

    url = f"{UPLOAD_BASE_URL}/api/file-stream-upload"
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        data = aiohttp.FormData()
        data.add_field("file", file_bytes, filename=filename, content_type=content_type)
        data.add_field("uploadPath", upload_path)

        async with session.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            data=data,
        ) as response:
            response_text = await response.text()

            if response.status != 200:
                raise Exception(f"Kie file upload HTTP {response.status}: {response_text[:300]}")

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                raise Exception(f"Kie file upload invalid JSON: {response_text[:300]}")

            if result.get("code") != 200:
                raise Exception(f"Kie file upload error: {result.get('msg', 'Unknown')}")

            resp_data = result.get("data", {}) or {}
            file_url = resp_data.get("downloadUrl") or resp_data.get("fileUrl")
            if not file_url:
                raise Exception(f"No downloadUrl in Kie upload response: {response_text[:300]}")

            logger.info("kie_file_uploaded", filename=filename, content_type=content_type, url=file_url)
            return file_url
