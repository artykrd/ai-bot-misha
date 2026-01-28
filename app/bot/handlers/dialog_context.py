"""
Dialog context management for tracking active user dialogs.
Now uses Redis for persistence and scalability under load.
"""
import json
from typing import Optional, Dict, Any
from app.core.logger import get_logger
from app.core.billing_config import get_text_model_billing

logger = get_logger(__name__)

# Dialog TTL in seconds (30 minutes - dialogs auto-expire if inactive)
DIALOG_TTL_SECONDS = 1800

# Redis key prefix for dialogs
DIALOG_KEY_PREFIX = "dialog:active:"


def _get_redis_client():
    """Get Redis client lazily to avoid circular imports."""
    from app.core.redis_client import redis_client
    return redis_client


# Model ID to AI service mapping with new billing system
MODEL_MAPPINGS = {
    324: {
        "name": "GPT 4.1 Mini",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "billing_id": "gpt-4.1-mini",  # New billing config ID
        "cost_per_request": 500,  # Legacy fallback
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    325: {
        "name": "GPT 4o",
        "provider": "openai",
        "model_id": "gpt-4o",
        "billing_id": "gpt-4o",
        "cost_per_request": 1000,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    326: {
        "name": "O3 Mini",
        "provider": "openai",
        "model_id": "o3-mini",
        "billing_id": "o3-mini",
        "cost_per_request": 700,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True
    },
    327: {
        "name": "Deepseek Chat",
        "provider": "deepseek",
        "model_id": "deepseek-chat",
        "billing_id": "deepseek-chat",
        "cost_per_request": 600,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True
    },
    328: {
        "name": "Deepseek R1",
        "provider": "deepseek",
        "model_id": "deepseek-reasoner",
        "billing_id": "deepseek-r1",
        "cost_per_request": 800,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True
    },
    329: {
        "name": "Gemini Flash 2.0",
        "provider": "google",
        "model_id": "gemini-2.0-flash-001",
        "billing_id": "gemini-flash-2.0",
        "cost_per_request": 400,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    330: {
        "name": "nano Banana",
        "provider": "google",
        "model_id": "gemini-2.0-flash-exp",
        "billing_id": "nano-banana-text",
        "cost_per_request": 900,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    331: {
        "name": "Sonar с поиском",
        "provider": "perplexity",
        "model_id": "sonar",
        "billing_id": "sonar",
        "cost_per_request": 700,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": False
    },
    332: {
        "name": "Sonar Pro",
        "provider": "perplexity",
        "model_id": "sonar-pro",
        "billing_id": "sonar-pro",
        "cost_per_request": 1000,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": False
    },
    333: {
        "name": "Claude 4",
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-20250514",
        "billing_id": "claude-4",
        "cost_per_request": 1200,
        "supports_vision": True,
        "supports_voice": False,
        "supports_files": True
    },
    334: {
        "name": "Claude 3.5 Haiku",
        "provider": "anthropic",
        "model_id": "claude-3-5-haiku-20241022",
        "billing_id": "claude-4",  # Using claude-4 billing for now
        "cost_per_request": 600,
        "supports_vision": True,
        "supports_voice": False,
        "supports_files": True
    },
    338: {
        "name": "GPT 4o-mini",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "billing_id": "gpt-4.1-mini",
        "cost_per_request": 250,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    335: {
        "name": "Анализ текста",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "billing_id": "gpt-4.1-mini",
        "cost_per_request": 500,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True,
        "system_prompt": "Ты - эксперт по анализу текста. Проводи глубокий анализ предоставленного текста."
    },
    336: {
        "name": "Генератор промптов",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "billing_id": "gpt-4.1-mini",
        "cost_per_request": 500,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True,
        "system_prompt": "Ты - эксперт по созданию эффективных промптов для AI моделей. Помогай создавать качественные промпты."
    },
    337: {
        "name": "GPT 5 Mini",
        "provider": "openai",
        "model_id": "gpt-4o-mini",  # Fallback to 4o-mini until GPT-5 is available
        "billing_id": "gpt-5-mini",
        "cost_per_request": 600,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
}


def _validate_model_mappings() -> None:
    """Validate dialog -> billing mapping to prevent silent mismatches."""
    for dialog_id, config in MODEL_MAPPINGS.items():
        billing_id = config.get("billing_id", config.get("model_id"))
        if not get_text_model_billing(billing_id):
            logger.error(
                "invalid_dialog_billing_mapping",
                dialog_id=dialog_id,
                billing_id=billing_id,
                model_id=config.get("model_id"),
                model_name=config.get("name"),
            )


_validate_model_mappings()


async def set_active_dialog(user_id: int, dialog_id: int, history_enabled: bool = False, show_costs: bool = False) -> bool:
    """Set active dialog for user in Redis with TTL."""
    if dialog_id not in MODEL_MAPPINGS:
        logger.warning(f"Unknown dialog_id: {dialog_id}")
        return False

    model_config = MODEL_MAPPINGS[dialog_id]

    dialog_data = {
        "dialog_id": dialog_id,
        "model_name": model_config["name"],
        "provider": model_config["provider"],
        "model_id": model_config["model_id"],
        "billing_id": model_config.get("billing_id", model_config["model_id"]),
        "cost_per_request": model_config["cost_per_request"],
        "history_enabled": history_enabled,
        "show_costs": show_costs,
        "supports_vision": model_config.get("supports_vision", False),
        "supports_voice": model_config.get("supports_voice", False),
        "supports_files": model_config.get("supports_files", False),
        "system_prompt": model_config.get("system_prompt"),
    }

    try:
        redis = _get_redis_client()
        key = f"{DIALOG_KEY_PREFIX}{user_id}"
        await redis.set_json(key, dialog_data, expire=DIALOG_TTL_SECONDS)
        logger.info(f"Active dialog set for user {user_id}: dialog_id={dialog_id}, model={model_config['name']}")
        return True
    except Exception as e:
        logger.error(f"Failed to set active dialog in Redis: {e}")
        return False


def get_active_dialog(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get active dialog for user from Redis.
    Note: This is a sync wrapper that runs the async version.
    For handlers, use get_active_dialog_async directly.
    """
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, we need to use the async version
        # This sync version is for backward compatibility
        return None  # Return None in sync context - use async version
    except RuntimeError:
        # No running loop, can't get dialog
        return None


async def get_active_dialog_async(user_id: int) -> Optional[Dict[str, Any]]:
    """Get active dialog for user from Redis (async version)."""
    try:
        redis = _get_redis_client()
        key = f"{DIALOG_KEY_PREFIX}{user_id}"
        dialog_data = await redis.get_json(key)
        if dialog_data:
            # Refresh TTL on access to keep active dialogs alive
            await redis.expire(key, DIALOG_TTL_SECONDS)
        return dialog_data
    except Exception as e:
        logger.error(f"Failed to get active dialog from Redis: {e}")
        return None


async def clear_active_dialog(user_id: int) -> bool:
    """Clear active dialog for user from Redis."""
    try:
        redis = _get_redis_client()
        key = f"{DIALOG_KEY_PREFIX}{user_id}"
        await redis.delete(key)
        logger.info(f"Clearing active dialog for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear active dialog from Redis: {e}")
        return False


async def update_dialog_settings(user_id: int, history_enabled: bool = None, show_costs: bool = None) -> bool:
    """Update dialog settings in Redis."""
    try:
        dialog = await get_active_dialog_async(user_id)
        if not dialog:
            return False

        if history_enabled is not None:
            dialog["history_enabled"] = history_enabled
        if show_costs is not None:
            dialog["show_costs"] = show_costs

        redis = _get_redis_client()
        key = f"{DIALOG_KEY_PREFIX}{user_id}"
        await redis.set_json(key, dialog, expire=DIALOG_TTL_SECONDS)
        return True
    except Exception as e:
        logger.error(f"Failed to update dialog settings in Redis: {e}")
        return False


async def has_active_dialog(user_id: int) -> bool:
    """Check if user has active dialog in Redis."""
    try:
        redis = _get_redis_client()
        key = f"{DIALOG_KEY_PREFIX}{user_id}"
        return await redis.exists(key)
    except Exception as e:
        logger.error(f"Failed to check active dialog in Redis: {e}")
        return False
