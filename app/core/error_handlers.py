"""
Unified error handling for AI services and user-facing error messages.
Provides user-friendly error messages without exposing technical details.
"""
import re
from typing import Optional, Tuple
from app.core.logger import get_logger

logger = get_logger(__name__)


# Error patterns for classification
ERROR_PATTERNS = {
    # Rate limits
    "rate_limit": [
        r"rate.?limit",
        r"429",
        r"too many requests",
        r"quota exceeded",
        r"RESOURCE_EXHAUSTED",
        r"requests per minute",
        r"RateLimitError",
    ],
    # Billing/quota issues
    "billing": [
        r"insufficient.?(funds|balance|credits|quota)",
        r"billing",
        r"payment required",
        r"credit",
        r"out of.?(credits|quota)",
        r"exceeded.?quota",
        r"balance.*exhausted",
        r"no.?available.?credits",
        r"402",
    ],
    # Authentication
    "auth": [
        r"invalid.?api.?key",
        r"authentication",
        r"unauthorized",
        r"401",
        r"403",
        r"permission.?denied",
        r"access.?denied",
    ],
    # Timeout
    "timeout": [
        r"timeout",
        r"timed.?out",
        r"deadline.?exceeded",
        r"request took too long",
        r"504",
        r"408",
    ],
    # Content filtering
    "content_filter": [
        r"content.?filter",
        r"policy.?violation",
        r"safety",
        r"inappropriate",
        r"blocked",
        r"moderation",
        r"rai.*filter",
    ],
    # Model unavailable
    "model_unavailable": [
        r"model.?(not|unavailable|disabled)",
        r"service.?unavailable",
        r"503",
        r"502",
        r"temporarily.?unavailable",
        r"maintenance",
    ],
    # Input validation
    "input_error": [
        r"invalid.?(input|prompt|request)",
        r"too (long|large|big)",
        r"exceeds.?(limit|maximum)",
        r"validation.?error",
        r"400",
    ],
    # Network errors
    "network": [
        r"network.?error",
        r"connection.?(failed|refused|reset|error)",
        r"dns",
        r"ssl",
        r"certificate",
        r"ECONNREFUSED",
        r"ETIMEDOUT",
    ],
}

# User-friendly messages for each error type
USER_MESSAGES = {
    "rate_limit": (
        "Превышен лимит запросов к нейросети. "
        "Подождите несколько минут и попробуйте снова."
    ),
    "billing": (
        "Временно недоступно: закончился лимит нейросети. "
        "Попробуйте позже или выберите другую модель."
    ),
    "auth": (
        "Ошибка конфигурации сервиса. "
        "Пожалуйста, сообщите в поддержку."
    ),
    "timeout": (
        "Запрос выполнялся слишком долго. "
        "Попробуйте ещё раз или упростите запрос."
    ),
    "content_filter": (
        "Запрос был заблокирован фильтрами безопасности. "
        "Попробуйте переформулировать запрос."
    ),
    "model_unavailable": (
        "Модель временно недоступна. "
        "Попробуйте позже или выберите другую модель."
    ),
    "input_error": (
        "Некорректный запрос. "
        "Проверьте формат данных и попробуйте снова."
    ),
    "network": (
        "Проблема с подключением к сервису. "
        "Попробуйте через несколько минут."
    ),
    "unknown": (
        "Произошла ошибка при обработке запроса. "
        "Попробуйте ещё раз."
    ),
}


def classify_error(error_message: str) -> str:
    """
    Classify error message into a category.

    Args:
        error_message: Raw error message from service

    Returns:
        Error category string
    """
    error_lower = error_message.lower()

    for category, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, error_lower, re.IGNORECASE):
                return category

    return "unknown"


def format_user_error(
    error: Exception | str,
    provider: str = "AI",
    model: str = None,
    user_id: int = None,
    request_id: str = None
) -> str:
    """
    Format error for user display, hiding technical details.
    Also logs the error with appropriate level.

    Args:
        error: Exception or error message string
        provider: AI provider name (for logging)
        model: Model name (for logging)
        user_id: User ID (for logging)
        request_id: Request ID for tracing (for logging)

    Returns:
        User-friendly error message
    """
    error_str = str(error)
    category = classify_error(error_str)

    # Log context
    log_context = {
        "provider": provider,
        "model": model,
        "user_id": user_id,
        "request_id": request_id,
        "error_category": category,
        "raw_error": error_str[:500],  # Truncate for logging
    }

    # Determine log level based on category
    if category == "billing":
        logger.critical(
            "llm_billing_error",
            **log_context,
            alert=True
        )
    elif category in ("auth", "model_unavailable"):
        logger.error(
            "llm_service_error",
            **log_context,
            alert=True
        )
    elif category == "rate_limit":
        logger.warning(
            "llm_rate_limit",
            **log_context
        )
    elif category in ("timeout", "network"):
        logger.warning(
            "llm_connectivity_error",
            **log_context
        )
    else:
        logger.error(
            "llm_error",
            **log_context
        )

    return USER_MESSAGES.get(category, USER_MESSAGES["unknown"])


def format_ai_error_with_suggestion(
    error: Exception | str,
    provider: str = "AI",
    model: str = None,
    user_id: int = None,
    suggest_alternatives: bool = True
) -> str:
    """
    Format error with alternative suggestions for the user.

    Args:
        error: Exception or error message
        provider: AI provider name
        model: Model name
        user_id: User ID
        suggest_alternatives: Whether to suggest alternative models

    Returns:
        Formatted error message with suggestions
    """
    base_message = format_user_error(error, provider, model, user_id)

    error_str = str(error).lower()
    category = classify_error(error_str)

    # Add specific suggestions based on error type
    suggestions = []

    if category == "billing" and suggest_alternatives:
        suggestions.append(
            "\n\nАльтернативные модели:\n"
            "- GPT-4o Mini (экономичная)\n"
            "- Gemini Flash (быстрая)\n"
            "- DeepSeek Chat (бюджетная)"
        )
    elif category == "content_filter":
        suggestions.append(
            "\n\nСоветы:\n"
            "- Избегайте упоминания реальных людей\n"
            "- Используйте абстрактные описания\n"
            "- Попробуйте мультяшный стиль"
        )
    elif category == "timeout":
        suggestions.append(
            "\n\nСоветы:\n"
            "- Сократите запрос\n"
            "- Попробуйте более быструю модель"
        )

    return base_message + "".join(suggestions)


def is_billing_error(error: Exception | str) -> bool:
    """Check if error is related to billing/quota."""
    return classify_error(str(error)) == "billing"


def is_rate_limit_error(error: Exception | str) -> bool:
    """Check if error is a rate limit."""
    return classify_error(str(error)) == "rate_limit"


def is_retryable_error(error: Exception | str) -> bool:
    """Check if error is potentially retryable."""
    category = classify_error(str(error))
    return category in ("rate_limit", "timeout", "network", "model_unavailable")


def get_retry_delay(error: Exception | str, attempt: int = 1) -> int:
    """
    Get suggested retry delay in seconds based on error type.

    Args:
        error: Error message or exception
        attempt: Current attempt number (for exponential backoff)

    Returns:
        Suggested delay in seconds
    """
    category = classify_error(str(error))

    base_delays = {
        "rate_limit": 60,  # Wait a minute for rate limits
        "timeout": 5,
        "network": 10,
        "model_unavailable": 30,
    }

    base_delay = base_delays.get(category, 5)
    # Exponential backoff with jitter
    return min(base_delay * (2 ** (attempt - 1)), 300)  # Max 5 minutes
