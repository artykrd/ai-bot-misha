"""
YooKassa payment service for processing payments.
"""
import hashlib
import hmac
import ipaddress
import os
import uuid
from typing import Optional, Dict, Any
from decimal import Decimal

from yookassa import Configuration, Payment as YooKassaPayment

from app.core.logger import get_logger
from app.core.config import settings
from app.core.log_safety import sanitise_body

logger = get_logger(__name__)


# Official YooKassa webhook source IPs (https://yookassa.ru/developers/using-api/webhooks).
# Used as a default allow-list when the operator hasn't configured custom IPs.
YOOKASSA_DEFAULT_NETWORKS = (
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11/32",
    "77.75.156.35/32",
    "77.75.154.128/25",
    "2a02:5180::/32",
)


def _parse_networks(values):
    """Parse a list of IPs/CIDRs into ip_network objects, ignoring invalid entries."""
    nets = []
    for raw in values:
        try:
            nets.append(ipaddress.ip_network(raw, strict=False))
        except ValueError:
            logger.warning("yookassa_invalid_allowed_ip", value=raw)
    return nets


def is_yookassa_source_ip(client_ip: Optional[str]) -> bool:
    """
    Check whether the given client IP belongs to YooKassa's webhook source range.

    Operators can override the list via YUKASSA_WEBHOOK_ALLOWED_IPS in .env.
    Returns True when the IP is missing only if the allow-list is empty
    (so the check can be a no-op in dev environments).
    """
    allowed = settings.yukassa_webhook_allowed_ips or list(YOOKASSA_DEFAULT_NETWORKS)
    networks = _parse_networks(allowed)
    if not networks:
        return True
    if not client_ip:
        return False
    try:
        ip = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(ip in net for net in networks)


def verify_yookassa_signature(raw_body: bytes, signature_header: Optional[str]) -> bool:
    """
    Verify HMAC-SHA256 signature of a YooKassa webhook payload.

    YooKassa supports an optional shared secret configured in the merchant
    account. If `YUKASSA_WEBHOOK_SECRET` is empty, this returns True (the
    operator opted out of cryptographic validation; IP allow-listing is then
    the only protection).
    """
    secret = settings.yukassa_webhook_secret
    if not secret:
        return True
    if not signature_header:
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    # Accept both "sha256=<hex>" and bare hex for forward compatibility.
    candidate = signature_header.split("=", 1)[-1].strip()
    return hmac.compare_digest(expected, candidate)


class YooKassaService:
    """Service for handling YooKassa payments."""

    def __init__(self):
        """Initialize YooKassa configuration."""
        self.shop_id = os.getenv("YUKASSA_SHOP_ID")
        self.secret_key = os.getenv("YUKASSA_SECRET_KEY")
        self.return_url = os.getenv("PAYMENT_RETURN_URL", "https://t.me/assistantvirtualsbot")

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

            # Limit description to 128 characters as per YooKassa API requirements
            truncated_description = description[:128] if len(description) > 128 else description

            # Create receipt for 54-FZ compliance
            # Note: Using phone as placeholder - YooKassa will collect email on payment form
            receipt = {
                "customer": {
                    "phone": "+79000000000"  # Placeholder - YooKassa will ask user for email on payment form
                },
                "items": [
                    {
                        "description": truncated_description,
                        "quantity": "1.00",
                        "amount": {
                            "value": str(amount),
                            "currency": "RUB"
                        },
                        "vat_code": 1,  # без НДС
                        "payment_subject": "service",  # Услуга/подписка
                        "payment_mode": "full_payment"  # Полная оплата
                    }
                ]
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
                "description": truncated_description,
                "receipt": receipt,  # Required for 54-FZ compliance
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
                "amount": float(amount),  # Convert Decimal to float for JSON serialization
                "currency": "RUB",
                "confirmation_url": payment.confirmation.confirmation_url,
                "created_at": str(payment.created_at) if payment.created_at else None,
                "metadata": payment_metadata
            }

        except Exception as e:
            # Get detailed error information
            error_detail = str(e)
            error_type = type(e).__name__

            # Try to extract response details if it's an HTTP error
            response_text = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    response_text = e.response.text if hasattr(e.response, 'text') else str(e.response)
                except:
                    pass

            logger.error(
                "yookassa_create_payment_error",
                error=error_detail,
                error_type=error_type,
                response=response_text,
                amount=amount,
                user_id=user_telegram_id,
                description=truncated_description if 'truncated_description' in locals() else description[:50]
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
                "amount": float(payment.amount.value),  # Convert to float for JSON serialization
                "currency": payment.amount.currency,
                "paid": payment.paid,
                "created_at": str(payment.created_at) if payment.created_at else None,
                "captured_at": str(payment.captured_at) if payment.captured_at else None,
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
        Parse a YooKassa webhook payload that has already been authenticated.

        Authentication (HMAC signature + IP allow-list) is performed by the
        HTTP handler before this method is called. This method is responsible
        only for normalising the payload into the dict the rest of the code
        consumes.

        Args:
            webhook_data: Webhook data from YooKassa (already parsed JSON)

        Returns:
            Processed payment data or None if failed
        """
        if not self.configured:
            logger.error("yookassa_webhook_failed", error="YooKassa not configured")
            return None

        try:
            # Parse webhook manually (no SDK signature validation)
            if not isinstance(webhook_data, dict):
                logger.error("yookassa_webhook_invalid_type", type=type(webhook_data).__name__)
                return None

            event = webhook_data.get("event")
            obj = webhook_data.get("object")

            if not event or not isinstance(obj, dict):
                logger.error(
                    "yookassa_webhook_missing_fields",
                    has_event=bool(event),
                    has_object=isinstance(obj, dict)
                )
                return None

            # Extract payment info
            payment_id = obj.get("id")
            status = obj.get("status")
            paid = obj.get("paid", False)
            amount = None

            if isinstance(obj.get("amount"), dict):
                try:
                    amount = float(obj["amount"]["value"])
                except Exception:
                    amount = None

            metadata = obj.get("metadata") or {}

            logger.info(
                "yookassa_webhook_parsed",
                webhook_event=event,
                payment_id=payment_id,
                status=status,
                paid=paid
            )

            return {
                "event": event,
                "payment_id": payment_id,
                "status": status,
                "paid": paid,
                "amount": amount,
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(
                "yookassa_webhook_error",
                error=str(e),
                webhook_data=sanitise_body(webhook_data),
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
