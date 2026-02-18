"""
Payment service for managing payment operations in the database.
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models.payment import Payment
from app.database.models.user import User
from app.database.models.subscription import Subscription
from app.services.payment.yookassa_service import YooKassaService
from app.core.logger import get_logger

logger = get_logger(__name__)


class PaymentService:
    """Service for managing payments."""

    def __init__(self, session: AsyncSession):
        """
        Initialize payment service.

        Args:
            session: Database session
        """
        self.session = session
        self.yookassa = YooKassaService()

    async def create_payment(
        self,
        user_id: int,
        amount: Decimal,
        description: str,
        subscription_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Payment]:
        """
        Create a new payment.

        Args:
            user_id: User ID
            amount: Payment amount in RUB
            description: Payment description
            subscription_id: Optional subscription ID
            metadata: Optional metadata

        Returns:
            Payment object or None if failed
        """
        # Get user
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.error("payment_create_failed", error="User not found", user_id=user_id)
            return None

        # Create payment in YooKassa
        yookassa_data = self.yookassa.create_payment(
            amount=amount,
            description=description,
            user_telegram_id=user.telegram_id,
            metadata=metadata
        )

        if not yookassa_data:
            # Don't log as ERROR here since yookassa_service already logged the detailed error
            logger.warning("payment_create_failed", error="YooKassa payment creation failed", user_id=user_id)
            return None

        # Create payment record in database
        import uuid
        payment = Payment(
            payment_id=f"PAY-{uuid.uuid4().hex[:16].upper()}",
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            currency="RUB",
            status="pending",
            yukassa_payment_id=yookassa_data["id"],
            yukassa_response=yookassa_data
        )

        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)

        logger.info(
            "payment_created",
            payment_id=payment.payment_id,
            user_id=user_id,
            amount=amount,
            yukassa_id=yookassa_data["id"]
        )

        return payment

    async def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """
        Get payment by ID.

        Args:
            payment_id: Payment ID

        Returns:
            Payment object or None
        """
        result = await self.session.execute(
            select(Payment).where(Payment.payment_id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_payment_by_yukassa_id(self, yukassa_payment_id: str) -> Optional[Payment]:
        """
        Get payment by YooKassa payment ID.

        Args:
            yukassa_payment_id: YooKassa payment ID

        Returns:
            Payment object or None
        """
        result = await self.session.execute(
            select(Payment).where(Payment.yukassa_payment_id == yukassa_payment_id)
        )
        return result.scalar_one_or_none()

    async def update_payment_status(
        self,
        payment_id: str,
        status: str,
        payment_method: Optional[str] = None,
        yukassa_response: Optional[Dict[str, Any]] = None
    ) -> Optional[Payment]:
        """
        Update payment status.

        Args:
            payment_id: Payment ID
            status: New status (pending, success, failed, refunded)
            payment_method: Payment method used
            yukassa_response: Updated YooKassa response

        Returns:
            Updated payment or None
        """
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            logger.error("payment_update_failed", error="Payment not found", payment_id=payment_id)
            return None

        payment.status = status
        if payment_method:
            payment.payment_method = payment_method
        if yukassa_response:
            payment.yukassa_response = yukassa_response

        await self.session.commit()
        await self.session.refresh(payment)

        logger.info(
            "payment_status_updated",
            payment_id=payment_id,
            status=status
        )

        return payment

    async def process_successful_payment(self, payment: Payment) -> bool:
        """
        Process successful payment - activate subscription or add tokens.

        Args:
            payment: Payment object

        Returns:
            True if processed successfully
        """
        try:
            from app.services.subscription import SubscriptionService

            logger.info(
                "process_successful_payment_started",
                payment_id=payment.payment_id,
                user_id=payment.user_id,
                current_status=payment.status,
                amount=float(payment.amount)
            )

            # Check if payment already processed (idempotency)
            if payment.status == "success":
                logger.info(
                    "payment_already_processed",
                    payment_id=payment.payment_id,
                    user_id=payment.user_id
                )
                return True

            subscription_service = SubscriptionService(self.session)

            # Get metadata from payment
            metadata = payment.yukassa_response.get("metadata") or {} if payment.yukassa_response else {}
            payment_type = metadata.get("type", "eternal_tokens")
            tokens_added = 0

            logger.info(
                "process_payment_metadata_parsed",
                payment_id=payment.payment_id,
                payment_type=payment_type,
                metadata=metadata
            )

            if payment_type == "eternal_tokens":
                logger.info(
                    "processing_eternal_tokens",
                    payment_id=payment.payment_id,
                    user_id=payment.user_id
                )
                # Add eternal tokens to user
                try:
                    tokens = int(metadata.get("tokens", 0))
                except (TypeError, ValueError):
                    tokens = 0

                if tokens > 0:
                    logger.info(
                        "adding_eternal_tokens",
                        user_id=payment.user_id,
                        tokens=tokens
                    )

                    subscription = await subscription_service.add_eternal_tokens(payment.user_id, tokens)
                    tokens_added = tokens

                    # Link payment to subscription and store price for refund
                    payment.subscription_id = subscription.id
                    subscription.price = payment.amount
                    await self.session.commit()

                    logger.info(
                        "eternal_tokens_added_to_db",
                        user_id=payment.user_id,
                        tokens=tokens,
                        subscription_id=subscription.id,
                        type="eternal"
                    )
                else:
                    logger.warning(
                        "eternal_tokens_zero_or_invalid",
                        user_id=payment.user_id,
                        tokens_value=tokens,
                        metadata=metadata
                    )

                # Award referrer if exists
                from app.services.referral import ReferralService

                referral_service = ReferralService(self.session)
                tokens_awarded, money_awarded = await referral_service.award_referrer_for_purchase(
                    referred_user_id=payment.user_id,
                    tokens_purchased=tokens,
                    money_paid=payment.amount
                )

                if tokens_awarded or money_awarded:
                    logger.info(
                        "referral_reward_awarded",
                        user_id=payment.user_id,
                        tokens_awarded=tokens_awarded,
                        money_awarded=money_awarded
                    )

            elif payment_type == "subscription":
                logger.info(
                    "processing_subscription",
                    payment_id=payment.payment_id,
                    user_id=payment.user_id
                )

                # Add subscription with tokens
                try:
                    days = int(metadata.get("days", 30))
                except (TypeError, ValueError):
                    days = 30

                tokens = metadata.get("tokens")
                if tokens is not None:
                    try:
                        tokens = int(tokens)
                    except (TypeError, ValueError):
                        tokens = 0

                logger.info(
                    "subscription_params_parsed",
                    user_id=payment.user_id,
                    days=days,
                    tokens=tokens
                )

                # Add subscription tokens
                if tokens and tokens > 0:
                    logger.info(
                        "adding_subscription_tokens",
                        user_id=payment.user_id,
                        tokens=tokens,
                        days=days
                    )

                    subscription = await subscription_service.add_subscription_tokens(
                        user_id=payment.user_id,
                        tokens=tokens,
                        days=days,
                        subscription_type="premium_subscription"
                    )
                    tokens_added = tokens

                    # Link payment to subscription and store price for refund
                    payment.subscription_id = subscription.id
                    subscription.price = payment.amount
                    await self.session.commit()

                    logger.info(
                        "subscription_tokens_added_to_db",
                        user_id=payment.user_id,
                        subscription_id=subscription.id,
                        days=days,
                        tokens=tokens
                    )
                else:
                    logger.warning(
                        "subscription_tokens_zero_or_invalid",
                        user_id=payment.user_id,
                        tokens_value=tokens,
                        days=days,
                        metadata=metadata
                    )

                # Award referrer if exists
                from app.services.referral import ReferralService

                referral_service = ReferralService(self.session)
                tokens_awarded, money_awarded = await referral_service.award_referrer_for_purchase(
                    referred_user_id=payment.user_id,
                    tokens_purchased=tokens or 0,
                    money_paid=payment.amount
                )

                if tokens_awarded or money_awarded:
                    logger.info(
                        "referral_reward_awarded_subscription",
                        user_id=payment.user_id,
                        tokens_awarded=tokens_awarded,
                        money_awarded=money_awarded
                    )

            # Update payment status
            logger.info(
                "updating_payment_status_to_success",
                payment_id=payment.payment_id,
                user_id=payment.user_id,
                tokens_added=tokens_added
            )

            payment.status = "success"
            if metadata.get("payment_method"):
                payment.payment_method = metadata.get("payment_method")
            await self.session.commit()

            logger.info(
                "payment_status_updated_successfully",
                payment_id=payment.payment_id,
                user_id=payment.user_id,
                new_status="success"
            )

            logger.info(
                "process_successful_payment_completed",
                payment_id=payment.payment_id,
                user_id=payment.user_id,
                tokens_added=tokens_added,
                payment_type=payment_type
            )

            return True

        except Exception as e:
            import traceback

            logger.error(
                "payment_processing_failed",
                error=str(e),
                error_type=type(e).__name__,
                payment_id=payment.payment_id,
                user_id=payment.user_id if hasattr(payment, 'user_id') else 'unknown',
                traceback=traceback.format_exc()
            )
            await self.session.rollback()
            return False

    async def get_user_payments(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> list[Payment]:
        """
        Get user payments.

        Args:
            user_id: User ID
            limit: Limit
            offset: Offset

        Returns:
            List of payments
        """
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def cancel_subscription_with_refund(
        self,
        subscription_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Cancel subscription and refund based on unused tokens.

        Args:
            subscription_id: Subscription ID
            user_id: User ID

        Returns:
            Dictionary with cancellation info or None if failed
        """
        try:
            # Get subscription
            result = await self.session.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            subscription = result.scalar_one_or_none()

            if not subscription:
                logger.error("subscription_not_found", subscription_id=subscription_id)
                return None

            # Check if subscription belongs to user
            if subscription.user_id != user_id:
                logger.error("subscription_access_denied", subscription_id=subscription_id, user_id=user_id)
                return None

            # Get payment for this subscription
            result = await self.session.execute(
                select(Payment).where(
                    Payment.subscription_id == subscription_id,
                    Payment.status == "success"
                )
            )
            payment = result.scalar_one_or_none()

            if not payment or not payment.yukassa_payment_id:
                logger.warning("payment_not_found_cancelling_without_refund", subscription_id=subscription_id)
                # Still cancel the subscription even if no payment found (e.g., eternal tokens)
                subscription.is_active = False
                await self.session.commit()

                total_tokens = subscription.tokens_amount
                used_tokens = subscription.tokens_used
                unused_tokens = max(0, total_tokens - used_tokens)

                return {
                    "subscription_id": subscription_id,
                    "total_tokens": total_tokens,
                    "used_tokens": used_tokens,
                    "unused_tokens": unused_tokens,
                    "original_price": float(subscription.price) if subscription.price else 0,
                    "refund_amount": 0,
                    "refunded": False,
                    "refund_error": "Платёж не найден. Подписка отменена без возврата."
                }

            # Calculate refund amount based on unused tokens or remaining time
            total_tokens = subscription.tokens_amount
            used_tokens = subscription.tokens_used
            unused_tokens = max(0, total_tokens - used_tokens)

            original_price = Decimal(str(subscription.price)) if subscription.price else Decimal("0")

            # If unlimited subscription, calculate refund based on remaining time
            if subscription.is_unlimited:
                if subscription.expires_at and subscription.started_at and original_price > 0:
                    from datetime import datetime, timezone
                    now = datetime.now(timezone.utc)
                    total_duration = (subscription.expires_at - subscription.started_at).total_seconds()
                    remaining_duration = max(0, (subscription.expires_at - now).total_seconds())
                    if total_duration > 0:
                        refund_percentage = remaining_duration / total_duration
                        refund_amount = Decimal(str(float(original_price) * refund_percentage))
                        refund_amount = refund_amount.quantize(Decimal("0.01"))
                    else:
                        refund_amount = Decimal("0")
                else:
                    refund_amount = Decimal("0")
                logger.info(
                    "unlimited_subscription_refund_calculated",
                    subscription_id=subscription_id,
                    refund_amount=float(refund_amount)
                )
            # If eternal subscription or token-based, calculate based on unused tokens
            elif subscription.is_eternal or total_tokens > 0:
                usage_percentage = used_tokens / total_tokens if total_tokens > 0 else 1.0
                refund_percentage = max(0, 1.0 - usage_percentage)
                refund_amount = Decimal(str(float(original_price) * refund_percentage))
                # Round to 2 decimal places
                refund_amount = refund_amount.quantize(Decimal("0.01"))
            else:
                refund_amount = Decimal("0")

            # Minimum refund is 10 rubles, otherwise not worth processing
            if refund_amount < Decimal("10.00"):
                refund_amount = Decimal("0")

            cancellation_info = {
                "subscription_id": subscription_id,
                "total_tokens": total_tokens,
                "used_tokens": used_tokens,
                "unused_tokens": unused_tokens,
                "original_price": float(subscription.price),
                "refund_amount": float(refund_amount),
                "refunded": False
            }

            # Process refund if amount > 0
            if refund_amount > Decimal("0"):
                refund_result = self.yookassa.refund_payment(
                    payment_id=payment.yukassa_payment_id,
                    amount=refund_amount,
                    reason=f"Отмена подписки. Использовано {used_tokens} из {total_tokens} токенов."
                )

                if refund_result:
                    # Update payment status
                    payment.status = "refunded"
                    await self.session.commit()

                    cancellation_info["refunded"] = True
                    cancellation_info["refund_id"] = refund_result.get("refund_id")

                    logger.info(
                        "subscription_refunded",
                        subscription_id=subscription_id,
                        refund_amount=float(refund_amount),
                        refund_id=refund_result.get("refund_id")
                    )
                else:
                    logger.error("refund_failed", subscription_id=subscription_id)
                    cancellation_info["refund_error"] = "Failed to process refund"

            # Deactivate subscription
            subscription.is_active = False
            await self.session.commit()

            logger.info(
                "subscription_cancelled",
                subscription_id=subscription_id,
                user_id=user_id,
                refund_amount=float(refund_amount)
            )

            return cancellation_info

        except Exception as e:
            logger.error(
                "subscription_cancellation_failed",
                error=str(e),
                subscription_id=subscription_id,
                user_id=user_id
            )
            await self.session.rollback()
            return None
