"""
FSM States for media generation (video, audio, image).
"""
from aiogram.fsm.state import State, StatesGroup
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KlingSettings:
    """Kling video generation settings stored in FSM."""
    version: str = "2.5"  # UI version: "2.1", "2.1 Pro", "2.5", "2.6"
    duration: int = 5  # 5 or 10 seconds
    aspect_ratio: str = "1:1"  # "1:1", "16:9", "9:16"
    auto_translate: bool = True  # Auto-translate prompt to English
    images: List[str] = field(default_factory=list)  # List of image paths (0-2 images)

    def to_dict(self) -> dict:
        """Convert to dict for FSM storage."""
        return {
            "kling_version": self.version,
            "kling_duration": self.duration,
            "kling_aspect_ratio": self.aspect_ratio,
            "kling_auto_translate": self.auto_translate,
            "kling_images": self.images,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KlingSettings":
        """Create from FSM data dict."""
        return cls(
            version=data.get("kling_version", "2.5"),
            duration=data.get("kling_duration", 5),
            aspect_ratio=data.get("kling_aspect_ratio", "1:1"),
            auto_translate=data.get("kling_auto_translate", True),
            images=data.get("kling_images", []),
        )

    def get_display_settings(self) -> str:
        """Get formatted settings string for display."""
        parts = []
        parts.append(f"Длительность: {self.duration} секунд")
        parts.append(f"Формат видео: {self.aspect_ratio}")
        parts.append(f"Версия: {self.version}")
        parts.append(f"Автоперевод: {'включен' if self.auto_translate else 'выключен'}")
        return "\n".join(parts)


@dataclass
class KlingImageSettings:
    """Kling image generation settings stored in FSM."""
    model: str = "kling-v1"  # Model: "kling-v1", "kling-v1-5", "kling-v2"
    aspect_ratio: str = "1:1"  # "1:1", "16:9", "9:16", "4:3", "3:4"
    resolution: str = "1k"  # "1k", "2k"
    auto_translate: bool = True  # Auto-translate prompt to English

    def to_dict(self) -> dict:
        """Convert to dict for FSM storage."""
        return {
            "kling_image_model": self.model,
            "kling_image_aspect_ratio": self.aspect_ratio,
            "kling_image_resolution": self.resolution,
            "kling_image_auto_translate": self.auto_translate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KlingImageSettings":
        """Create from FSM data dict."""
        return cls(
            model=data.get("kling_image_model", "kling-v1"),
            aspect_ratio=data.get("kling_image_aspect_ratio", "1:1"),
            resolution=data.get("kling_image_resolution", "1k"),
            auto_translate=data.get("kling_image_auto_translate", True),
        )

    def get_display_settings(self) -> str:
        """Get formatted settings string for display."""
        model_names = {
            "kling-v1": "Kling v1",
            "kling-v1-5": "Kling v1.5",
            "kling-v2": "Kling v2",
        }
        parts = []
        parts.append(f"Модель: {model_names.get(self.model, self.model)}")
        parts.append(f"Формат: {self.aspect_ratio}")
        parts.append(f"Разрешение: {self.resolution}")
        parts.append(f"Автоперевод: {'включен' if self.auto_translate else 'выключен'}")
        return "\n".join(parts)


@dataclass
class SoraSettings:
    """Sora 2 video generation settings stored in FSM."""
    quality: str = "stable"  # "stable" or "pro"
    duration: int = 10  # 10 or 15 seconds
    aspect_ratio: str = "landscape"  # "landscape" or "portrait"

    def to_dict(self) -> dict:
        """Convert to dict for FSM storage."""
        return {
            "sora_quality": self.quality,
            "sora_duration": self.duration,
            "sora_aspect_ratio": self.aspect_ratio,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SoraSettings":
        """Create from FSM data dict."""
        return cls(
            quality=data.get("sora_quality", "stable"),
            duration=data.get("sora_duration", 10),
            aspect_ratio=data.get("sora_aspect_ratio", "landscape"),
        )

    def get_display_settings(self) -> str:
        """Get formatted settings string for display."""
        quality_names = {
            "stable": "Стандартное (Stable)",
            "pro": "Высокое (Pro 720P)",
        }
        aspect_names = {
            "landscape": "16:9 (альбомный)",
            "portrait": "9:16 (портретный)",
        }
        parts = []
        parts.append(f"Длительность: {self.duration} сек.")
        parts.append(f"Качество: {quality_names.get(self.quality, self.quality)}")
        parts.append(f"Формат: {aspect_names.get(self.aspect_ratio, self.aspect_ratio)}")
        return "\n".join(parts)

    def get_api_model(self, has_image: bool = False) -> str:
        """Get API model name based on settings and mode."""
        if self.quality == "pro":
            return "sora-2-image-to-video" if has_image else "sora-2-text-to-video"
        else:
            return "sora-2-image-to-video-stable" if has_image else "sora-2-text-to-video-stable"


class MediaState(StatesGroup):
    """States for media generation."""
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()
    waiting_for_whisper_audio = State()
    waiting_for_vision_image = State()
    waiting_for_vision_prompt = State()
    # Photo tools states
    waiting_for_photo_upscale = State()
    waiting_for_photo_replace_bg = State()
    waiting_for_photo_remove_bg = State()
    waiting_for_photo_vectorize = State()
    # Smart input handling states
    waiting_for_photo_action_choice = State()  # User sent photo, need to choose what to do
    # Background replacement states
    waiting_for_replace_bg_image = State()
    waiting_for_replace_bg_prompt = State()
    # Kling video generation states
    kling_waiting_for_prompt = State()  # Waiting for text prompt or image
    kling_waiting_for_images = State()  # Collecting images (for multi-image mode)


class SunoState(StatesGroup):
    """States for Suno music generation."""
    # Step-by-step creation states
    waiting_for_song_title = State()
    waiting_for_lyrics_choice = State()  # Choose: by title, by description, or write own
    waiting_for_lyrics_description = State()  # User describes the song
    waiting_for_lyrics_text = State()  # User provides lyrics text
    waiting_for_melody_prompt = State()  # For instrumental mode - melody description
    waiting_for_style = State()  # Waiting for style selection
