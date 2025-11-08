"""
Dialog context management for tracking active user dialogs.
"""
from typing import Optional, Dict, Any
from app.core.logger import get_logger

logger = get_logger(__name__)

# TODO: Move to Redis or database for persistence
# Format: {user_id: {"dialog_id": int, "model_id": str, "history_enabled": bool, "show_costs": bool}}
ACTIVE_DIALOGS: Dict[int, Dict[str, Any]] = {}


# Model ID to AI service mapping
MODEL_MAPPINGS = {
    324: {
        "name": "GPT 4.1 Mini",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "cost_per_request": 500,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    325: {
        "name": "GPT 4o",
        "provider": "openai",
        "model_id": "gpt-4o",
        "cost_per_request": 1000,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    326: {
        "name": "O3 Mini",
        "provider": "openai",
        "model_id": "o3-mini",
        "cost_per_request": 700,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True
    },
    327: {
        "name": "Deepseek Chat",
        "provider": "deepseek",
        "model_id": "deepseek-chat",
        "cost_per_request": 600,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True
    },
    328: {
        "name": "Deepseek R1",
        "provider": "deepseek",
        "model_id": "deepseek-reasoner",
        "cost_per_request": 800,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": True
    },
    329: {
        "name": "Gemini Flash 2.0",
        "provider": "google",
        "model_id": "gemini-2.0-flash-exp",
        "cost_per_request": 400,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    330: {
        "name": "Gemini Pro 2.5",
        "provider": "google",
        "model_id": "gemini-2.5-pro-preview",
        "cost_per_request": 900,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
    331: {
        "name": "Sonar с поиском",
        "provider": "perplexity",
        "model_id": "sonar",
        "cost_per_request": 700,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": False
    },
    332: {
        "name": "Sonar Pro",
        "provider": "perplexity",
        "model_id": "sonar-pro",
        "cost_per_request": 1000,
        "supports_vision": False,
        "supports_voice": False,
        "supports_files": False
    },
    333: {
        "name": "Claude 3.7",
        "provider": "anthropic",
        "model_id": "claude-3-7-sonnet-20250219",
        "cost_per_request": 1200,
        "supports_vision": True,
        "supports_voice": False,
        "supports_files": True
    },
    334: {
        "name": "Claude 3.5",
        "provider": "anthropic",
        "model_id": "claude-3-5-sonnet-20241022",
        "cost_per_request": 1000,
        "supports_vision": True,
        "supports_voice": False,
        "supports_files": True
    },
    335: {
        "name": "Анализ текста",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
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
        "cost_per_request": 600,
        "supports_vision": True,
        "supports_voice": True,
        "supports_files": True
    },
}


def set_active_dialog(user_id: int, dialog_id: int, history_enabled: bool = False, show_costs: bool = False):
    """Set active dialog for user."""
    if dialog_id not in MODEL_MAPPINGS:
        logger.warning(f"Unknown dialog_id: {dialog_id}")
        return False

    model_config = MODEL_MAPPINGS[dialog_id]

    ACTIVE_DIALOGS[user_id] = {
        "dialog_id": dialog_id,
        "model_name": model_config["name"],
        "provider": model_config["provider"],
        "model_id": model_config["model_id"],
        "cost_per_request": model_config["cost_per_request"],
        "history_enabled": history_enabled,
        "show_costs": show_costs,
        "supports_vision": model_config.get("supports_vision", False),
        "supports_voice": model_config.get("supports_voice", False),
        "supports_files": model_config.get("supports_files", False),
        "system_prompt": model_config.get("system_prompt"),
    }

    logger.info(f"Active dialog set for user {user_id}: dialog_id={dialog_id}, model={model_config['name']}")
    return True


def get_active_dialog(user_id: int) -> Optional[Dict[str, Any]]:
    """Get active dialog for user."""
    return ACTIVE_DIALOGS.get(user_id)


def clear_active_dialog(user_id: int):
    """Clear active dialog for user."""
    if user_id in ACTIVE_DIALOGS:
        logger.info(f"Clearing active dialog for user {user_id}")
        del ACTIVE_DIALOGS[user_id]


def update_dialog_settings(user_id: int, history_enabled: bool = None, show_costs: bool = None):
    """Update dialog settings."""
    if user_id not in ACTIVE_DIALOGS:
        return False

    if history_enabled is not None:
        ACTIVE_DIALOGS[user_id]["history_enabled"] = history_enabled
    if show_costs is not None:
        ACTIVE_DIALOGS[user_id]["show_costs"] = show_costs

    return True


def has_active_dialog(user_id: int) -> bool:
    """Check if user has active dialog."""
    return user_id in ACTIVE_DIALOGS
