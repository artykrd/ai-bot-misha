"""
Base AI provider interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class AIResponse:
    """Standard AI response format."""
    success: bool
    content: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAIProvider(ABC):
    """Base class for all AI providers."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text response."""
        pass

    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Generate image from prompt."""
        pass

    async def generate_video(self, prompt: str, **kwargs) -> AIResponse:
        """Generate video from prompt."""
        raise NotImplementedError("Video generation not supported by this provider")

    async def generate_audio(self, prompt: str, **kwargs) -> AIResponse:
        """Generate audio from prompt."""
        raise NotImplementedError("Audio generation not supported by this provider")

    async def transcribe_audio(self, audio_path: str, **kwargs) -> AIResponse:
        """Transcribe audio to text."""
        raise NotImplementedError("Audio transcription not supported by this provider")
