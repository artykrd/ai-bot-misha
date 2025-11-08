"""
Custom exceptions for the application.
"""


class AIBotException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(AIBotException):
    """Database-related errors."""
    pass


class UserNotFoundError(AIBotException):
    """User not found in database."""
    pass


class UserBannedError(AIBotException):
    """User is banned."""
    pass


class InsufficientTokensError(AIBotException):
    """User has insufficient tokens for the operation."""
    pass


class SubscriptionError(AIBotException):
    """Subscription-related errors."""
    pass


class SubscriptionExpiredError(SubscriptionError):
    """Subscription has expired."""
    pass


class PaymentError(AIBotException):
    """Payment processing errors."""
    pass


class PaymentFailedError(PaymentError):
    """Payment failed."""
    pass


class AIServiceError(AIBotException):
    """AI service errors."""
    pass


class AIProviderError(AIServiceError):
    """Error from AI provider API."""

    def __init__(self, provider: str, message: str, details: dict = None):
        self.provider = provider
        super().__init__(f"{provider}: {message}", details)


class AITimeoutError(AIServiceError):
    """AI request timeout."""
    pass


class AIRateLimitError(AIServiceError):
    """AI service rate limit exceeded."""
    pass


class FileStorageError(AIBotException):
    """File storage errors."""
    pass


class FileTooLargeError(FileStorageError):
    """File size exceeds maximum allowed."""
    pass


class InvalidFileTypeError(FileStorageError):
    """Invalid file type."""
    pass


class ReferralError(AIBotException):
    """Referral program errors."""
    pass


class PromocodeError(AIBotException):
    """Promocode errors."""
    pass


class PromocodeInvalidError(PromocodeError):
    """Invalid or expired promocode."""
    pass


class PromocodeAlreadyUsedError(PromocodeError):
    """Promocode already used by this user."""
    pass


class RateLimitExceededError(AIBotException):
    """Rate limit exceeded."""

    def __init__(self, limit: int, period: str = "hour"):
        message = f"Rate limit exceeded: {limit} requests per {period}"
        super().__init__(message, {"limit": limit, "period": period})


class ConfigurationError(AIBotException):
    """Configuration errors."""
    pass


class ValidationError(AIBotException):
    """Data validation errors."""
    pass
