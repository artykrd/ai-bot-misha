"""
Billing configuration for AI models.

This module defines token costs for all AI models in the system.
Token price: 1 token = 0.000588 RUB
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ModelType(str, Enum):
    """Model types for billing."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class TextModelBilling:
    """Billing configuration for text models (dynamic billing)."""
    base_tokens: int
    per_gpt_token: float
    display_name: str

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> int:
        """
        Calculate token cost for text generation.

        Formula: tokens_spent = base_tokens + (prompt_tokens + completion_tokens) * per_gpt_token

        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion

        Returns:
            Total tokens to charge
        """
        total_gpt_tokens = prompt_tokens + completion_tokens
        tokens_spent = self.base_tokens + int(total_gpt_tokens * self.per_gpt_token)
        return tokens_spent


@dataclass
class FixedModelBilling:
    """Billing configuration for image/video models (fixed billing)."""
    tokens_per_generation: int
    display_name: str
    description_suffix: str
    model_type: ModelType

    def get_cost(self) -> int:
        """Get fixed token cost."""
        return self.tokens_per_generation


# ==============================================
# TEXT MODELS (Dynamic billing)
# ==============================================
TEXT_MODELS: Dict[str, TextModelBilling] = {
    # GPT Models
    "gpt-4.1-mini": TextModelBilling(
        base_tokens=140,
        per_gpt_token=1.6,
        display_name="GPT-4.1 Mini"
    ),
    "gpt-4o": TextModelBilling(
        base_tokens=520,
        per_gpt_token=6.8,
        display_name="GPT-4o"
    ),
    "gpt-5-mini": TextModelBilling(
        base_tokens=170,
        per_gpt_token=1.8,
        display_name="GPT-5 Mini"
    ),

    # O3 Mini
    "o3-mini": TextModelBilling(
        base_tokens=260,
        per_gpt_token=3.1,
        display_name="O3 Mini"
    ),

    # DeepSeek Models
    "deepseek-chat": TextModelBilling(
        base_tokens=180,
        per_gpt_token=2.0,
        display_name="DeepSeek Chat"
    ),
    "deepseek-r1": TextModelBilling(
        base_tokens=300,
        per_gpt_token=3.4,
        display_name="DeepSeek R1"
    ),

    # Gemini Models
    "gemini-flash-2.0": TextModelBilling(
        base_tokens=130,
        per_gpt_token=1.3,
        display_name="Gemini Flash 2.0"
    ),

    # Nano Banana (text)
    "nano-banana-text": TextModelBilling(
        base_tokens=110,
        per_gpt_token=1.1,
        display_name="nano Banana (text)"
    ),

    # Perplexity Models
    "sonar": TextModelBilling(
        base_tokens=220,
        per_gpt_token=2.6,
        display_name="Sonar (with search)"
    ),
    "sonar-pro": TextModelBilling(
        base_tokens=260,
        per_gpt_token=3.0,
        display_name="Sonar Pro"
    ),

    # Claude Models
    "claude-4": TextModelBilling(
        base_tokens=320,
        per_gpt_token=3.6,
        display_name="Claude 4"
    ),
}


# Legacy model mappings (for backward compatibility)
LEGACY_TEXT_MODEL_MAP = {
    "gpt-4": "gpt-4o",
    "gpt-4-mini": "gpt-4.1-mini",
    "claude": "claude-4",
    "gemini": "gemini-flash-2.0",
    "deepseek": "deepseek-chat",
}


# ==============================================
# IMAGE MODELS (Fixed billing)
# ==============================================
IMAGE_MODELS: Dict[str, FixedModelBilling] = {
    "dalle3": FixedModelBilling(
        tokens_per_generation=9500,
        display_name="DALL·E 3",
        description_suffix="Стоимость генерации: 9 500 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "midjourney": FixedModelBilling(
        tokens_per_generation=13000,
        display_name="Midjourney",
        description_suffix="Стоимость генерации: 13 000 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "nano-banana-image": FixedModelBilling(
        tokens_per_generation=6000,
        display_name="Nano Banana",
        description_suffix="Стоимость генерации: 6 000 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "banana-pro": FixedModelBilling(
        tokens_per_generation=25000,
        display_name="Banana PRO",
        description_suffix="Стоимость генерации: 25 000 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "stable-diffusion": FixedModelBilling(
        tokens_per_generation=6000,
        display_name="Stable Diffusion",
        description_suffix="Стоимость генерации: 6 000 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "recraft": FixedModelBilling(
        tokens_per_generation=7000,
        display_name="Recraft",
        description_suffix="Стоимость генерации: 7 000 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "kling-image": FixedModelBilling(
        tokens_per_generation=6600,
        display_name="Kling AI",
        description_suffix="Стоимость генерации: 6 600 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "face-swap": FixedModelBilling(
        tokens_per_generation=11500,
        display_name="Face Swap",
        description_suffix="Стоимость операции: 11 500 токенов",
        model_type=ModelType.IMAGE
    ),
    "seedream-4.5": FixedModelBilling(
        tokens_per_generation=19300,
        display_name="Seedream 4.5",
        description_suffix="Стоимость генерации: 19 300 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
    "seedream-4.0": FixedModelBilling(
        tokens_per_generation=14500,
        display_name="Seedream 4.0",
        description_suffix="Стоимость генерации: 14 500 токенов за изображение",
        model_type=ModelType.IMAGE
    ),
}


# ==============================================
# VIDEO MODELS (Fixed billing)
# ==============================================
VIDEO_MODELS: Dict[str, FixedModelBilling] = {
    "sora2": FixedModelBilling(
        tokens_per_generation=50000,
        display_name="Sora 2",
        description_suffix="Стоимость генерации видео (10 секунд): 50 000 токенов",
        model_type=ModelType.VIDEO
    ),
    "veo-3.1-fast": FixedModelBilling(
        tokens_per_generation=115000,
        display_name="Veo 3.1 Fast",
        description_suffix="Стоимость генерации видео: 115 000 токенов",
        model_type=ModelType.VIDEO
    ),
    "midjourney-video-sd": FixedModelBilling(
        tokens_per_generation=75000,
        display_name="Midjourney Video SD",
        description_suffix="Стоимость генерации видео: 75 000 токенов",
        model_type=ModelType.VIDEO
    ),
    "midjourney-video-hd": FixedModelBilling(
        tokens_per_generation=225000,
        display_name="Midjourney Video HD",
        description_suffix="Стоимость генерации видео: 225 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Legacy Kling billing (kept for backward compatibility)
    "kling-video": FixedModelBilling(
        tokens_per_generation=58000,
        display_name="Kling 2.5",
        description_suffix="Стоимость генерации видео (5 секунд): 58 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Kling 2.1 / 2.1 Pro - 5 seconds
    "kling-2.1-5s": FixedModelBilling(
        tokens_per_generation=58000,
        display_name="Kling 2.1",
        description_suffix="Стоимость генерации видео (5 секунд): 58 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Kling 2.1 / 2.1 Pro - 10 seconds
    "kling-2.1-10s": FixedModelBilling(
        tokens_per_generation=115000,
        display_name="Kling 2.1",
        description_suffix="Стоимость генерации видео (10 секунд): 115 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Kling 2.5 - 5 seconds
    "kling-2.5-5s": FixedModelBilling(
        tokens_per_generation=58000,
        display_name="Kling 2.5",
        description_suffix="Стоимость генерации видео (5 секунд): 58 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Kling 2.5 - 10 seconds
    "kling-2.5-10s": FixedModelBilling(
        tokens_per_generation=115000,
        display_name="Kling 2.5",
        description_suffix="Стоимость генерации видео (10 секунд): 115 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Kling 2.6 - 5 seconds
    "kling-2.6-5s": FixedModelBilling(
        tokens_per_generation=238000,
        display_name="Kling 2.6",
        description_suffix="Стоимость генерации видео (5 секунд): 238 000 токенов",
        model_type=ModelType.VIDEO
    ),
    # Kling 2.6 - 10 seconds
    "kling-2.6-10s": FixedModelBilling(
        tokens_per_generation=475000,
        display_name="Kling 2.6",
        description_suffix="Стоимость генерации видео (10 секунд): 475 000 токенов",
        model_type=ModelType.VIDEO
    ),
    "kling-effects": FixedModelBilling(
        tokens_per_generation=99000,
        display_name="Kling Effects",
        description_suffix="Стоимость применения эффекта: 99 000 токенов",
        model_type=ModelType.VIDEO
    ),
    "hailuo": FixedModelBilling(
        tokens_per_generation=89500,
        display_name="Hailuo",
        description_suffix="Стоимость генерации видео: 89 500 токенов",
        model_type=ModelType.VIDEO
    ),
    "luma": FixedModelBilling(
        tokens_per_generation=85000,
        display_name="Luma",
        description_suffix="Стоимость генерации видео: 85 000 токенов",
        model_type=ModelType.VIDEO
    ),
}


# Legacy video model mappings
LEGACY_VIDEO_MODEL_MAP = {
    "veo": "veo-3.1-fast",
    "sora": "sora2",
}


# ==============================================
# KLING MODEL MAPPING
# ==============================================
# UI version -> API model_name mapping
KLING_VERSION_TO_API = {
    "2.1": "kling-v2-1-master",
    "2.1 Pro": "kling-v2-1-master",
    "2.5": "kling-v2-5-turbo",
    "2.6": "kling-v2-master",
}


def get_kling_billing_key(version: str, duration: int) -> str:
    """
    Get billing key for Kling based on version and duration.

    Args:
        version: UI version string (e.g., "2.1", "2.5", "2.6")
        duration: Duration in seconds (5 or 10)

    Returns:
        Billing key for VIDEO_MODELS dict
    """
    # Normalize version (remove "Pro" suffix for billing calculation since same price)
    version_normalized = version.replace(" Pro", "")
    duration_suffix = f"{duration}s"
    return f"kling-{version_normalized}-{duration_suffix}"


def get_kling_api_model(version: str) -> str:
    """
    Get API model_name from UI version.

    Args:
        version: UI version string (e.g., "2.1", "2.5", "2.6")

    Returns:
        API model_name string
    """
    return KLING_VERSION_TO_API.get(version, "kling-v2-5-turbo")


def get_kling_tokens_cost(version: str, duration: int) -> int:
    """
    Get token cost for Kling video generation.

    Args:
        version: UI version string (e.g., "2.1", "2.5", "2.6")
        duration: Duration in seconds (5 or 10)

    Returns:
        Token cost for this generation
    """
    billing_key = get_kling_billing_key(version, duration)
    billing = VIDEO_MODELS.get(billing_key)
    if billing:
        return billing.tokens_per_generation

    # Fallback to default kling-video
    return VIDEO_MODELS.get("kling-video", FixedModelBilling(
        tokens_per_generation=58000,
        display_name="Kling",
        description_suffix="",
        model_type=ModelType.VIDEO
    )).tokens_per_generation


# ==============================================
# TOKEN PACKAGES
# ==============================================
@dataclass
class TokenPackage:
    """Token package configuration."""
    days: int
    tokens: int
    price: float  # Price in RUB

    @property
    def price_per_token(self) -> float:
        """Calculate price per token."""
        return self.price / self.tokens if self.tokens > 0 else 0


# Token packages as specified in the task
TOKEN_PACKAGES = {
    "7days": TokenPackage(days=7, tokens=150000, price=88),
    "14days": TokenPackage(days=14, tokens=250000, price=176),
    "21days": TokenPackage(days=21, tokens=500000, price=260),
    "30days_1m": TokenPackage(days=30, tokens=1000000, price=537),
    "30days_5m": TokenPackage(days=30, tokens=5000000, price=2511),
}


# Token price constant
TOKEN_PRICE_RUB = 0.000588


# ==============================================
# HELPER FUNCTIONS
# ==============================================
def format_token_amount(tokens: int) -> str:
    """Format token amount with spaced thousands."""
    return f"{tokens:,}".replace(",", " ")


def get_text_model_billing(model_id: str) -> Optional[TextModelBilling]:
    """
    Get billing configuration for a text model.

    Args:
        model_id: Model identifier

    Returns:
        TextModelBilling object or None if not found
    """
    # Check legacy mappings first
    if model_id in LEGACY_TEXT_MODEL_MAP:
        model_id = LEGACY_TEXT_MODEL_MAP[model_id]

    return TEXT_MODELS.get(model_id)


def format_text_model_pricing(model_id: str) -> Optional[str]:
    """Format pricing info for text models."""
    billing = get_text_model_billing(model_id)
    if not billing:
        return None
    return (
        f"{billing.display_name} — база {format_token_amount(billing.base_tokens)} "
        f"+ {billing.per_gpt_token} за токен AI"
    )


def get_image_model_billing(model_id: str) -> Optional[FixedModelBilling]:
    """
    Get billing configuration for an image model.

    Args:
        model_id: Model identifier

    Returns:
        FixedModelBilling object or None if not found
    """
    return IMAGE_MODELS.get(model_id)


def get_video_model_billing(model_id: str) -> Optional[FixedModelBilling]:
    """
    Get billing configuration for a video model.

    Args:
        model_id: Model identifier

    Returns:
        FixedModelBilling object or None if not found
    """
    # Check legacy mappings first
    if model_id in LEGACY_VIDEO_MODEL_MAP:
        model_id = LEGACY_VIDEO_MODEL_MAP[model_id]

    return VIDEO_MODELS.get(model_id)


def calculate_text_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> Optional[int]:
    """
    Calculate cost for text generation.

    Args:
        model_id: Model identifier
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens

    Returns:
        Token cost or None if model not found
    """
    billing = get_text_model_billing(model_id)
    if billing:
        return billing.calculate_cost(prompt_tokens, completion_tokens)
    return None


def get_fixed_cost(model_id: str, model_type: ModelType) -> Optional[int]:
    """
    Get fixed cost for image/video generation.

    Args:
        model_id: Model identifier
        model_type: Type of model (IMAGE or VIDEO)

    Returns:
        Token cost or None if model not found
    """
    if model_type == ModelType.IMAGE:
        billing = get_image_model_billing(model_id)
    elif model_type == ModelType.VIDEO:
        billing = get_video_model_billing(model_id)
    else:
        return None

    if billing:
        return billing.get_cost()
    return None


def get_all_models() -> Dict[str, Any]:
    """
    Get all models configuration.

    Returns:
        Dictionary with all models grouped by type
    """
    return {
        "text": TEXT_MODELS,
        "image": IMAGE_MODELS,
        "video": VIDEO_MODELS,
    }


def tokens_to_rub(tokens: int) -> float:
    """
    Convert tokens to rubles.

    Args:
        tokens: Number of tokens

    Returns:
        Price in RUB
    """
    return tokens * TOKEN_PRICE_RUB


def rub_to_tokens(rub: float) -> int:
    """
    Convert rubles to tokens.

    Args:
        rub: Price in RUB

    Returns:
        Number of tokens
    """
    return int(rub / TOKEN_PRICE_RUB)
