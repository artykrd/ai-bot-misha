"""
Base audio service interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass
from pathlib import Path
import aiohttp
from datetime import datetime

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AudioResponse:
    """Standard audio generation/processing response format."""
    success: bool
    audio_path: Optional[str] = None
    text: Optional[str] = None  # For transcription
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAudioProvider(ABC):
    """Base class for audio providers."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.storage_path = Path(settings.storage_path) / "audio"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def generate_audio(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> AudioResponse:
        """Generate audio from prompt."""
        pass

    async def transcribe(
        self,
        audio_path: str,
        **kwargs
    ) -> AudioResponse:
        """Transcribe audio to text."""
        raise NotImplementedError("Transcription not supported by this provider")

    async def _download_file(self, url: str, filename: str) -> str:
        """Download file from URL to storage."""
        try:
            file_path = self.storage_path / filename

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())

                        logger.info(
                            "audio_downloaded",
                            url=url,
                            path=str(file_path),
                            size=file_path.stat().st_size
                        )
                        return str(file_path)
                    else:
                        raise Exception(f"Failed to download: HTTP {response.status}")
        except Exception as e:
            logger.error("audio_download_failed", error=str(e), url=url)
            raise

    def _generate_filename(self, extension: str = "mp3") -> str:
        """Generate unique filename for audio."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"audio_{timestamp}.{extension}"
