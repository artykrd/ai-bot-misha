"""
Unified notification messages for media generation.
"""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import escape_md
from typing import Optional
import uuid


def format_generation_message(
    content_type: str,
    model_name: str,
    tokens_used: int,
    user_tokens: int,
    prompt: str,
    mode: str = None
) -> str:
    """
    Format a unified generation success message.

    Args:
        content_type: Type of content (видео, изображение, музыку)
        model_name: Name of the model/service used
        tokens_used: Number of tokens used for this request
        user_tokens: User's remaining tokens
        prompt: The prompt used for generation
        mode: Optional mode info (e.g., "text-to-video", "image-to-video")

    Returns:
        Formatted message string
    """
    mode_info = f" ({mode})" if mode else ""

    # Escape special Markdown characters in prompt
    escaped_prompt = escape_md(prompt[:150])
    prompt_suffix = '...' if len(prompt) > 150 else ''

    message = (
        f"✅ Сгенерировал {content_type} по вашему запросу в {model_name}{mode_info}.\n\n"
        f"💰 Запрос стоил: {tokens_used:,} токенов\n"
        f"📊 Остаток: {user_tokens:,} токенов\n\n"
        f"📝 Промпт: {escaped_prompt}{prompt_suffix}"
    )

    return message


def create_action_keyboard(
    action_text: str,
    action_callback: str,
    file_path: Optional[str] = None,
    file_type: str = "file"
) -> InlineKeyboardBuilder:
    """
    Create a standard keyboard with action, download, and home buttons.

    Args:
        action_text: Text for the action button (e.g., "🎬 Создать новое видео")
        action_callback: Callback data for the action button
        file_path: Optional file path to enable download button
        file_type: Type of file ('image' or 'video') for download

    Returns:
        InlineKeyboardBuilder instance
    """
    from app.bot.utils.file_cache import file_cache

    builder = InlineKeyboardBuilder()
    builder.button(text=action_text, callback_data=action_callback)

    # Add download button if file path is provided
    if file_path:
        # Generate unique cache key
        cache_key = f"{file_type}:{uuid.uuid4().hex[:12]}"
        file_cache.store(cache_key, file_path)

        builder.button(
            text="📥 Скачать оригинал",
            callback_data=f"download:{cache_key}"
        )

    builder.button(text="🏠 В главное меню", callback_data="main_menu")
    builder.adjust(1)  # 1 button per row

    return builder


# Content type translations
CONTENT_TYPES = {
    "video": "видео",
    "image": "изображение",
    "audio": "музыку",
}

# Model-specific action buttons configuration
MODEL_ACTIONS = {
    "veo": {
        "text": "🎬 Создать новое видео",
        "callback": "bot.veo"
    },
    "sora": {
        "text": "🎬 Создать новое видео",
        "callback": "bot.sora"
    },
    "luma": {
        "text": "🎬 Создать новое видео",
        "callback": "bot.luma"
    },
    "hailuo": {
        "text": "🎬 Создать новое видео",
        "callback": "bot.hailuo"
    },
    "kling": {
        "text": "🎬 Создать новое видео",
        "callback": "bot.kling_video"
    },
    "kling_effects": {
        "text": "🎬 Создать новое видео",
        "callback": "bot.kling_effects"
    },
    "gpt_image": {
        "text": "🎨 Создать новое изображение",
        "callback": "bot.gpt_image"
    },
    "nano_banana": {
        "text": "🎨 Создать новое изображение",
        "callback": "bot.nano"
    },
    "dalle": {
        "text": "🎨 Создать новое изображение",
        "callback": "bot.gpt_image"
    },
    "suno": {
        "text": "🎵 Создать новую музыку",
        "callback": "bot.suno"
    },
}
