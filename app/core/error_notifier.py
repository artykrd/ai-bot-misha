"""
Error notification system for admin bot.
Sends error notifications to administrators when critical errors occur.
"""
import logging
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from aiogram import Bot

from app.core.config import settings


class ErrorNotifier:
    """
    Handles error notifications to admin bot.
    Includes throttling to prevent spam.
    Uses separate admin bot token for notifications.
    """

    def __init__(self):
        self.bot: Optional[Bot] = None
        self.last_notification_time = defaultdict(lambda: datetime.min)
        self.notification_cooldown = timedelta(minutes=5)  # 5 minutes between same error notifications
        self.error_counts = defaultdict(int)
        self._initialize_bot()

    def _initialize_bot(self):
        """Initialize admin bot using admin bot token from settings."""
        try:
            if settings.telegram_admin_bot_token:
                self.bot = Bot(token=settings.telegram_admin_bot_token)
                logging.info("Error notifier initialized with admin bot")
        except Exception as e:
            logging.warning(f"Failed to initialize admin bot for error notifications: {e}")

    def set_bot(self, bot: Bot):
        """
        Set the bot instance for sending notifications.
        Note: This is deprecated, bot is now initialized from settings.
        """
        # Keep for backwards compatibility but don't use
        pass

    async def notify_admins(self, error_type: str, error_message: str, details: str = ""):
        """
        Send error notification to all admins.

        Args:
            error_type: Type of error (e.g., "Nano Banana", "Referral", "Database")
            error_message: Short error description
            details: Additional details about the error
        """
        if not self.bot or not settings.admin_user_ids:
            return

        # Filter out user-facing errors that are not technical issues
        # These errors are expected and part of normal operation
        user_facing_error_patterns = [
            "Не удалось сгенерировать изображение. Это может быть из-за:",
            "• Сложности промпта или референсного изображения",
            "• Технической проблемы на стороне API",
            "• Несовместимости параметров",
            # Safety filter / content policy errors
            "Генерация заблокирована фильтром безопасности",
            "фильтром безопасности",
            "API не сгенерировал изображение",
            "Попробуйте изменить промпт",
            "FinishReason.PROHIBITED_CONTENT",
            "PROHIBITED_CONTENT",
            "Генерация прервана",
            "причина: FinishReason",
            "content_policy_violation",
            "safety_filter",
            "Your request was rejected",
            "blocked by safety",
        ]

        # Check if error message contains user-facing error text
        full_error_text = f"{error_message} {details}".replace("\\", "")
        for pattern in user_facing_error_patterns:
            if pattern in full_error_text:
                # This is a user-facing error, not a technical issue - don't notify
                logging.debug(f"Skipping notification for user-facing error: {error_message[:50]}")
                return

        # Create error key for throttling
        error_key = f"{error_type}:{error_message[:50]}"

        # Check if we should send notification (throttling)
        now = datetime.now()
        last_time = self.last_notification_time[error_key]

        if now - last_time < self.notification_cooldown:
            # Just increment counter, don't send
            self.error_counts[error_key] += 1
            return

        # Update last notification time
        self.last_notification_time[error_key] = now

        # Get accumulated count if any
        count = self.error_counts[error_key]
        count_text = f" (повторилось {count + 1} раз)" if count > 0 else ""
        self.error_counts[error_key] = 0  # Reset counter

        # Escape markdown special characters
        def escape_markdown(text: str) -> str:
            """Escape markdown special characters."""
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text

        # Format message with escaped content
        safe_error_type = escape_markdown(str(error_type))
        safe_error_message = escape_markdown(str(error_message))
        safe_details = escape_markdown(str(details)) if details else 'Нет дополнительных деталей'

        message = f"""🚨 *Ошибка в боте*{count_text}

📁 *Модуль:* {safe_error_type}
❌ *Ошибка:* {safe_error_message}

📝 *Подробности:*
{safe_details}

🕐 *Время:* {now.strftime('%Y-%m-%d %H:%M:%S')}

💡 *Действие:* Проверьте логи в logs/error\\.log"""

        # Send to all admins
        for admin_id in settings.admin_user_ids:
            try:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode="Markdown"
                )
            except Exception as e:
                # Can't send notification, just log it
                logging.error(f"Failed to send error notification to admin {admin_id}: {e}")


# Global instance
error_notifier = ErrorNotifier()


class ErrorNotificationHandler(logging.Handler):
    """
    Custom logging handler that sends ERROR and CRITICAL level logs to admin bot.
    """

    def __init__(self, notifier: ErrorNotifier):
        super().__init__(level=logging.ERROR)
        self.notifier = notifier

    def emit(self, record: logging.LogRecord):
        """Handle log record and send notification if needed."""
        try:
            # Increment error counter for monitoring
            try:
                from app.monitoring.daily_report import daily_report_generator
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    loop.create_task(daily_report_generator.increment_error_count())
                except RuntimeError:
                    pass
            except Exception:
                pass

            # Extract module information
            module_name = record.name.split('.')[-1] if record.name else "Unknown"

            # Map module names to user-friendly names
            module_mapping = {
                "nano_banana_service": "Nano Banana",
                "dalle_service": "DALL-E",
                "veo_service": "Veo",
                "sora_service": "Sora",
                "suno_service": "Suno",
                "referral": "Реферальная программа",
                "subscription_service": "Система подписок",
                "payment": "Платежная система",
                "database": "База данных",
            }

            error_type = module_mapping.get(module_name, module_name.title())

            # Get error message
            error_message = record.getMessage()

            # Get stack trace if available
            details = ""
            if record.exc_info:
                import traceback
                details = ''.join(traceback.format_exception(*record.exc_info))
                # Limit details to 500 characters
                if len(details) > 500:
                    details = details[:500] + "\n... (truncated)"

            # Send notification asynchronously
            # Create a task to avoid blocking
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(
                    self.notifier.notify_admins(error_type, error_message, details)
                )
            except RuntimeError:
                # No event loop running, skip notification
                pass

        except Exception:
            # Don't let handler errors break the application
            self.handleError(record)


def setup_error_notifications(bot: Bot):
    """
    Setup error notification system.

    Args:
        bot: Bot instance for sending notifications
    """
    error_notifier.set_bot(bot)

    # Add handler to root logger
    handler = ErrorNotificationHandler(error_notifier)
    logging.getLogger().addHandler(handler)
