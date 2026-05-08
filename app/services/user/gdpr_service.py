"""
GDPR / 152-ФЗ helpers.

Provides the building blocks for the right-to-erasure (delete account) and
right-to-access (export personal data) flows. The actual user-facing entry
points live in `app/bot/handlers/gdpr.py`; the admin tools can also reuse
this service.
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.database.models.user import User
from app.database.models.subscription import Subscription
from app.database.models.payment import Payment
from app.database.models.ai_request import AIRequest
from app.database.models.dialog import Dialog
from app.database.models.referral import Referral
from app.database.models.video_job import VideoGenerationJob
from app.database.models.file import File as FileModel

logger = get_logger(__name__)


class GDPRService:
    """Right-to-erasure and right-to-access helpers."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_user_data(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Build a JSON-serialisable snapshot of all data we hold about the user.

        Returns None when no user is found.
        """
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user: Optional[User] = result.scalar_one_or_none()
        if not user:
            return None

        subscriptions: List[Dict[str, Any]] = []
        for sub in user.subscriptions:
            subscriptions.append({
                "id": sub.id,
                "subscription_type": sub.subscription_type,
                "tokens_amount": sub.tokens_amount,
                "tokens_used": sub.tokens_used,
                "price": float(sub.price) if sub.price is not None else 0.0,
                "is_active": sub.is_active,
                "started_at": sub.started_at.isoformat() if sub.started_at else None,
                "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
            })

        payments: List[Dict[str, Any]] = []
        for payment in user.payments:
            payments.append({
                "payment_id": payment.payment_id,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "status": payment.status,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
            })

        ai_requests_count = await self.session.scalar(
            select(func.count(AIRequest.id)).where(AIRequest.user_id == user.id)
        ) or 0

        return {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_activity": user.last_activity.isoformat() if user.last_activity else None,
            },
            "subscriptions": subscriptions,
            "payments": payments,
            "ai_requests_total": ai_requests_count,
            "dialogs_total": len(user.dialogs),
            "video_jobs_total": len(user.video_jobs),
        }

    async def export_user_data_json(self, telegram_id: int) -> Optional[str]:
        """JSON-encoded variant of `export_user_data` for direct download."""
        snapshot = await self.export_user_data(telegram_id)
        if snapshot is None:
            return None
        return json.dumps(snapshot, ensure_ascii=False, indent=2)

    async def delete_user(self, telegram_id: int) -> bool:
        """
        Hard-delete a user and all derived rows (right to erasure).

        Returns False when the user can't be found. Cleans up rows whose FKs
        were declared with ondelete='SET NULL' and would otherwise dangle.
        """
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user: Optional[User] = result.scalar_one_or_none()
        if not user:
            return False

        user_id = user.id

        try:
            # Drop rows the FK cascade misses (some tables use SET NULL).
            await self.session.execute(
                delete(VideoGenerationJob).where(VideoGenerationJob.user_id == user_id)
            )
            await self.session.execute(
                delete(FileModel).where(FileModel.user_id == user_id)
            )
            await self.session.execute(
                delete(AIRequest).where(AIRequest.user_id == user_id)
            )
            await self.session.execute(
                delete(Dialog).where(Dialog.user_id == user_id)
            )
            await self.session.execute(
                delete(Subscription).where(Subscription.user_id == user_id)
            )
            await self.session.execute(
                delete(Payment).where(Payment.user_id == user_id)
            )
            await self.session.execute(
                delete(Referral).where(
                    (Referral.referrer_id == user_id) | (Referral.referred_id == user_id)
                )
            )

            await self.session.delete(user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            logger.exception("gdpr_delete_user_failed", user_id=user_id)
            raise

        logger.info(
            "gdpr_user_deleted",
            user_id=user_id,
            telegram_id=telegram_id,
        )
        return True
