"""
YooKassa payment service for processing payments.
"""
import os
import uuid
from typing import Optional, Dict, Any
from decimal import Decimal

from yookassa import Configuration, Payment as YooKassaPayment
from yookassa.domain.notification import WebhookNotification

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class YooKassaService:
    """Service for handling YooKassa payments."""

    def __init__(self):
        """Initialize YooKassa configuration."""
        self.shop_id = os.getenv("YUKASSA_SHOP_ID")
        self.secret_key = os.getenv("YUKASSA_SECRET_KEY")
        self.return_url = os.getenv("PAYMENT_RETURN_URL", "https://t.me/GPTchatneiroseti_BOT")

        if not self.shop_id or not self.secret_key:
            logger.warning(
                "yookassa_not_configured",
                message="YooKassa credentials not found in environment"
            )
            self.configured = False
        else:
            # Configure YooKassa SDK
            Configuration.account_id = self.shop_id
            Configuration.secret_key = self.secret_key
            self.configured = True
            logger.info("yookassa_configured", shop_id=self.shop_id[:6] + "...")

    def create_payment(
        self,
        amount: Decimal,
        description: str,
        user_telegram_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a payment in YooKassa.

        Args:
            amount: Payment amount in RUB
            description: Payment description
            user_telegram_id: Telegram user ID
            metadata: Additional metadata to attach to payment

        Returns:
            Dictionary with payment data or None if failed
        """
        if not self.configured:
            logger.error("yookassa_create_payment_failed", error="YooKassa not configured")
            return None

        try:
            # Generate unique idempotency key
            idempotency_key = str(uuid.uuid4())

            # Prepare metadata
            payment_metadata = {
                "user_telegram_id": str(user_telegram_id),
                **(metadata or {})
            }

            # Create payment
            payment = YooKassaPayment.create({
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.return_url
                },
                "capture": True,  # Auto-capture payment
                "description": description,
                "metadata": payment_metadata
            }, idempotency_key)

            logger.info(
                "yookassa_payment_created",
                payment_id=payment.id,
                amount=amount,
                user_id=user_telegram_id
            )

            return {
                "id": payment.id,
                "status": payment.status,
                "amount": amount,
                "currency": "RUB",
                "confirmation_url": payment.confirmation.confirmation_url,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "metadata": payment_metadata
            }

        except Exception as e:
            logger.error(
                "yookassa_create_payment_error",
                error=str(e),
                amount=amount,
                user_id=user_telegram_id
            )
            return None

    def get_payment_info(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment information from YooKassa.

        Args:
            payment_id: YooKassa payment ID

        Returns:
            Dictionary with payment data or None if failed
        """
        if not self.configured:
            logger.error("yookassa_get_payment_failed", error="YooKassa not configured")
            return None

        try:
            payment = YooKassaPayment.find_one(payment_id)

            if not payment:
                logger.warning("yookassa_payment_not_found", payment_id=payment_id)
                return None

            return {
                "id": payment.id,
                "status": payment.status,
                "amount": Decimal(payment.amount.value),
                "currency": payment.amount.currency,
                "paid": payment.paid,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "captured_at": payment.captured_at.isoformat() if payment.captured_at else None,
                "metadata": payment.metadata if payment.metadata else {}
            }

        except Exception as e:
            logger.error(
                "yookassa_get_payment_error",
                error=str(e),
                payment_id=payment_id
            )
            return None

    def process_webhook(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process YooKassa webhook notification.

        Args:
            webhook_data: Webhook data from YooKassa

        Returns:
            Processed payment data or None if failed
        """
        if not self.configured:
            logger.error("yookassa_webhook_failed", error="YooKassa not configured")
            return None

        try:
            # Parse webhook notification
            notification = WebhookNotification(webhook_data)
            payment = notification.object

            logger.info(
                "yookassa_webhook_received",
                event=notification.event,
                payment_id=payment.id,
                status=payment.status
            )

            return {
                "event": notification.event,
                "payment_id": payment.id,
                "status": payment.status,
                "amount": Decimal(payment.amount.value),
                "currency": payment.amount.currency,
                "paid": payment.paid,
                "metadata": payment.metadata if payment.metadata else {}
            }

        except Exception as e:
            logger.error(
                "yookassa_webhook_error",
                error=str(e),
                webhook_data=webhook_data
            )
            return None

    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Refund a payment.

        Args:
            payment_id: YooKassa payment ID
            amount: Refund amount (None for full refund)
            reason: Refund reason

        Returns:
            Dictionary with refund data or None if failed
        """
        if not self.configured:
            logger.error("yookassa_refund_failed", error="YooKassa not configured")
            return None

        try:
            from yookassa import Refund

            # Get payment info first
            payment_info = self.get_payment_info(payment_id)
            if not payment_info:
                logger.error("yookassa_refund_failed", error="Payment not found")
                return None

            # Determine refund amount
            refund_amount = amount or payment_info["amount"]

            # Create refund
            idempotency_key = str(uuid.uuid4())
            refund = Refund.create({
                "amount": {
                    "value": str(refund_amount),
                    "currency": payment_info["currency"]
                },
                "payment_id": payment_id,
                "description": reason or "Refund requested"
            }, idempotency_key)

            logger.info(
                "yookassa_refund_created",
                refund_id=refund.id,
                payment_id=payment_id,
                amount=refund_amount
            )

            return {
                "refund_id": refund.id,
                "status": refund.status,
                "amount": refund_amount,
                "payment_id": payment_id
            }

        except Exception as e:
            logger.error(
                "yookassa_refund_error",
                error=str(e),
                payment_id=payment_id
            )
            return None
