"""
Reporting Service for daily business analytics.

Generates and sends daily reports to admin Telegram bot.

Report period: 21:00 MSK (previous day) -> 21:00 MSK (today)
Report time: 09:00 MSK daily
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from decimal import Decimal

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot

from app.database.database import async_session_maker
from app.database.models.user import User
from app.database.models.subscription import Subscription
from app.database.models.payment import Payment
from app.database.models.ai_request import AIRequest
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Moscow timezone offset (UTC+3)
MSK_OFFSET = timedelta(hours=3)


class ReportingService:
    """
    Service for generating daily business reports.

    Reports include:
    - New subscriptions count and revenue
    - User statistics (total, new, active)
    - Daily and weekly revenue
    - AI costs analysis (when data is available)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_daily_report(self) -> Dict[str, Any]:
        """
        Generate daily business report.

        Report period: 21:00 MSK (previous day) -> 21:00 MSK (today)

        Returns:
            Dictionary with all report metrics
        """
        now_utc = datetime.now(timezone.utc)
        now_msk = now_utc + MSK_OFFSET

        # Calculate report period (21:00 -> 21:00 MSK)
        today_21_msk = now_msk.replace(hour=21, minute=0, second=0, microsecond=0)

        if now_msk.hour < 21:
            # Before 21:00 today - report for yesterday
            period_end_msk = today_21_msk
            period_start_msk = today_21_msk - timedelta(days=1)
        else:
            # After 21:00 today - report for today
            period_start_msk = today_21_msk
            period_end_msk = today_21_msk + timedelta(days=1)

        # Convert to UTC for database queries
        period_start = period_start_msk - MSK_OFFSET
        period_end = period_end_msk - MSK_OFFSET

        # 7-day period for weekly metrics
        week_start = period_start - timedelta(days=7)

        report = {
            "period_start": period_start_msk.strftime("%Y-%m-%d %H:%M"),
            "period_end": period_end_msk.strftime("%Y-%m-%d %H:%M"),
            "generated_at": now_msk.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": "MSK",
        }

        # 1. User statistics
        report["users"] = await self._get_user_stats(period_start, period_end)

        # 2. New subscriptions
        report["new_subscriptions"] = await self._get_new_subscriptions(period_start, period_end)

        # 3. Revenue (daily)
        report["daily_revenue"] = await self._get_revenue(period_start, period_end)

        # 4. Revenue (weekly)
        report["weekly_revenue"] = await self._get_revenue(week_start, period_end)

        # 5. AI costs (if data available)
        report["ai_costs"] = await self._get_ai_costs(period_start, period_end)

        # 6. Unlimited subscription analysis
        report["unlimited_analysis"] = await self._get_unlimited_analysis(period_start, period_end)

        return report

    async def _get_user_stats(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get user statistics."""

        # Total users
        total_query = select(func.count(User.id))
        total_result = await self.session.execute(total_query)
        total_users = total_result.scalar() or 0

        # New users in period
        new_query = select(func.count(User.id)).where(
            User.created_at >= period_start,
            User.created_at < period_end
        )
        new_result = await self.session.execute(new_query)
        new_users = new_result.scalar() or 0

        # Active users (made requests in period)
        active_query = select(func.count(func.distinct(AIRequest.user_id))).where(
            AIRequest.created_at >= period_start,
            AIRequest.created_at < period_end
        )
        active_result = await self.session.execute(active_query)
        active_users = active_result.scalar() or 0

        # "Old" users (registered > 7 days ago)
        week_ago = period_start - timedelta(days=7)
        old_query = select(func.count(User.id)).where(
            User.created_at < week_ago
        )
        old_result = await self.session.execute(old_query)
        old_users = old_result.scalar() or 0

        # Users with active subscriptions
        paying_query = select(func.count(func.distinct(Subscription.user_id))).where(
            Subscription.is_active == True
        )
        paying_result = await self.session.execute(paying_query)
        paying_users = paying_result.scalar() or 0

        return {
            "total": total_users,
            "new_today": new_users,
            "active_today": active_users,
            "old_users": old_users,
            "paying_users": paying_users,
        }

    async def _get_new_subscriptions(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get new subscriptions statistics."""

        # Total count and sum
        total_query = select(
            func.count(Subscription.id),
            func.coalesce(func.sum(Subscription.price), 0)
        ).where(
            Subscription.created_at >= period_start,
            Subscription.created_at < period_end
        )
        total_result = await self.session.execute(total_query)
        row = total_result.one()

        # By subscription type
        type_query = select(
            Subscription.subscription_type,
            func.count(Subscription.id),
            func.coalesce(func.sum(Subscription.price), 0)
        ).where(
            Subscription.created_at >= period_start,
            Subscription.created_at < period_end
        ).group_by(Subscription.subscription_type)

        type_result = await self.session.execute(type_query)
        by_type = {
            r[0]: {"count": r[1], "revenue": float(r[2])}
            for r in type_result.all()
        }

        return {
            "count": row[0] or 0,
            "total_amount": float(row[1] or 0),
            "by_type": by_type,
        }

    async def _get_revenue(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get revenue statistics from successful payments."""

        query = select(
            func.count(Payment.id),
            func.coalesce(func.sum(Payment.amount), 0)
        ).where(
            Payment.status == "success",
            Payment.created_at >= period_start,
            Payment.created_at < period_end
        )
        result = await self.session.execute(query)
        row = result.one()

        return {
            "payments_count": row[0] or 0,
            "total_amount": float(row[1] or 0),
        }

    async def _get_ai_costs(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Get AI API costs statistics.

        Note: This will return meaningful data only after
        handlers are updated to log operations with cost_usd.
        """

        # Check if we have any cost data
        has_cost_data_query = select(func.count(AIRequest.id)).where(
            AIRequest.created_at >= period_start,
            AIRequest.created_at < period_end,
            AIRequest.cost_usd.isnot(None)
        )
        has_cost_result = await self.session.execute(has_cost_data_query)
        requests_with_cost = has_cost_result.scalar() or 0

        # Total AI requests (regardless of cost tracking)
        total_query = select(
            func.count(AIRequest.id),
            func.coalesce(func.sum(AIRequest.tokens_cost), 0),
            func.coalesce(func.sum(AIRequest.cost_usd), 0),
            func.coalesce(func.sum(AIRequest.cost_rub), 0)
        ).where(
            AIRequest.created_at >= period_start,
            AIRequest.created_at < period_end,
            AIRequest.status == "completed"
        )
        total_result = await self.session.execute(total_query)
        row = total_result.one()

        # By category (only if we have category data)
        by_category = {}
        category_query = select(
            AIRequest.operation_category,
            func.count(AIRequest.id),
            func.coalesce(func.sum(AIRequest.tokens_cost), 0),
            func.coalesce(func.sum(AIRequest.cost_usd), 0)
        ).where(
            AIRequest.created_at >= period_start,
            AIRequest.created_at < period_end,
            AIRequest.status == "completed",
            AIRequest.operation_category.isnot(None)
        ).group_by(AIRequest.operation_category)

        category_result = await self.session.execute(category_query)
        for r in category_result.all():
            if r[0]:  # Skip None categories
                by_category[r[0]] = {
                    "count": r[1],
                    "tokens": r[2] or 0,
                    "cost_usd": float(r[3] or 0),
                }

        return {
            "total_requests": row[0] or 0,
            "requests_with_cost_tracking": requests_with_cost,
            "total_tokens": row[1] or 0,
            "total_cost_usd": float(row[2] or 0),
            "total_cost_rub": float(row[3] or 0),
            "by_category": by_category,
            "cost_tracking_enabled": requests_with_cost > 0,
        }

    async def _get_unlimited_analysis(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Analyze unlimited subscription costs.

        This provides insights into whether unlimited subscriptions
        are profitable based on actual usage.
        """

        # Requests from unlimited subscriptions
        query = select(
            func.count(AIRequest.id),
            func.coalesce(func.sum(AIRequest.tokens_cost), 0),
            func.coalesce(func.sum(AIRequest.cost_usd), 0),
            func.coalesce(func.sum(AIRequest.cost_rub), 0)
        ).where(
            AIRequest.created_at >= period_start,
            AIRequest.created_at < period_end,
            AIRequest.status == "completed",
            AIRequest.is_unlimited_subscription == True
        )
        result = await self.session.execute(query)
        row = result.one()

        # Count unique unlimited subscriptions used
        subs_query = select(
            func.count(func.distinct(AIRequest.subscription_id))
        ).where(
            AIRequest.created_at >= period_start,
            AIRequest.created_at < period_end,
            AIRequest.is_unlimited_subscription == True
        )
        subs_result = await self.session.execute(subs_query)
        unique_subs = subs_result.scalar() or 0

        total_cost_usd = float(row[2] or 0)
        total_cost_rub = float(row[3] or 0)

        # Calculate averages
        avg_cost_usd = total_cost_usd / unique_subs if unique_subs > 0 else 0
        avg_cost_rub = total_cost_rub / unique_subs if unique_subs > 0 else 0

        # Get unlimited subscription price (from subscription_plans)
        # Default to 649 RUB if not found
        unlimited_price = 649.0

        profit_per_sub = unlimited_price - avg_cost_rub if avg_cost_rub > 0 else None

        return {
            "requests_count": row[0] or 0,
            "total_tokens": row[1] or 0,
            "total_cost_usd": total_cost_usd,
            "total_cost_rub": total_cost_rub,
            "unique_subscriptions": unique_subs,
            "avg_cost_per_sub_usd": avg_cost_usd,
            "avg_cost_per_sub_rub": avg_cost_rub,
            "subscription_price_rub": unlimited_price,
            "avg_profit_per_sub_rub": profit_per_sub,
            "is_profitable": profit_per_sub > 0 if profit_per_sub is not None else None,
            "has_data": unique_subs > 0 and total_cost_rub > 0,
        }


def format_report_message(report: Dict[str, Any]) -> str:
    """
    Format report as Telegram message.

    Uses plain text to avoid Markdown escaping issues.
    """
    users = report.get("users", {})
    subs = report.get("new_subscriptions", {})
    daily = report.get("daily_revenue", {})
    weekly = report.get("weekly_revenue", {})
    costs = report.get("ai_costs", {})
    unlimited = report.get("unlimited_analysis", {})

    # Format subscriptions by type
    subs_by_type_lines = []
    for sub_type, data in subs.get("by_type", {}).items():
        subs_by_type_lines.append(
            f"    {sub_type}: {data['count']} / {data['revenue']:,.0f} RUB"
        )
    subs_by_type = "\n".join(subs_by_type_lines) if subs_by_type_lines else "    Нет"

    # Build message parts
    lines = [
        "ЕЖЕДНЕВНЫЙ БИЗНЕС-ОТЧЁТ",
        "",
        f"Период: {report.get('period_start', '')} - {report.get('period_end', '')} MSK",
        "",
        "=" * 35,
        "",
        "ПОЛЬЗОВАТЕЛИ",
        f"  Всего: {users.get('total', 0):,}",
        f"  Новых за период: {users.get('new_today', 0):,}",
        f"  Активных за период: {users.get('active_today', 0):,}",
        f"  С подпиской: {users.get('paying_users', 0):,}",
        "",
        "=" * 35,
        "",
        "НОВЫЕ ПОДПИСКИ",
        f"  Количество: {subs.get('count', 0)}",
        f"  Сумма: {subs.get('total_amount', 0):,.0f} RUB",
        "  По типам:",
        subs_by_type,
        "",
        "=" * 35,
        "",
        "ВЫРУЧКА",
        f"  За сутки: {daily.get('total_amount', 0):,.0f} RUB ({daily.get('payments_count', 0)} платежей)",
        f"  За 7 дней: {weekly.get('total_amount', 0):,.0f} RUB",
        "",
    ]

    # AI costs section (only if tracking is enabled)
    if costs.get("cost_tracking_enabled"):
        lines.extend([
            "=" * 35,
            "",
            "AI РАСХОДЫ",
            f"  Запросов: {costs.get('total_requests', 0):,}",
            f"  Токенов: {costs.get('total_tokens', 0):,}",
            f"  Себестоимость: ${costs.get('total_cost_usd', 0):,.2f} / {costs.get('total_cost_rub', 0):,.0f} RUB",
            "",
        ])

        # By category
        if costs.get("by_category"):
            lines.append("  По категориям:")
            for cat, data in costs["by_category"].items():
                lines.append(f"    {cat}: {data['count']} / ${data['cost_usd']:,.2f}")
            lines.append("")
    else:
        lines.extend([
            "=" * 35,
            "",
            "AI РАСХОДЫ",
            f"  Запросов: {costs.get('total_requests', 0):,}",
            "  Себестоимость: данные накапливаются...",
            "",
        ])

    # Unlimited analysis (only if we have data)
    if unlimited.get("has_data"):
        status = "Прибыльно" if unlimited.get("is_profitable") else "Убыточно"
        lines.extend([
            "=" * 35,
            "",
            "АНАЛИЗ БЕЗЛИМИТА",
            f"  Подписок использовано: {unlimited.get('unique_subscriptions', 0)}",
            f"  Запросов: {unlimited.get('requests_count', 0):,}",
            f"  Себестоимость: {unlimited.get('total_cost_rub', 0):,.0f} RUB",
            f"  Средняя на подписку: {unlimited.get('avg_cost_per_sub_rub', 0):,.0f} RUB",
            f"  Цена тарифа: {unlimited.get('subscription_price_rub', 649):,.0f} RUB",
            f"  Средняя прибыль: {unlimited.get('avg_profit_per_sub_rub', 0):,.0f} RUB",
            f"  Статус: {status}",
            "",
        ])

    lines.extend([
        "=" * 35,
        "",
        f"Сгенерировано: {report.get('generated_at', '')} MSK",
    ])

    return "\n".join(lines)


async def send_daily_business_report() -> bool:
    """
    Generate and send daily business report to admin bot.

    This function should be scheduled to run daily at 09:00 MSK (06:00 UTC).

    Returns:
        True if report was sent successfully
    """
    logger.info("generating_daily_business_report")

    try:
        # Generate report
        async with async_session_maker() as session:
            service = ReportingService(session)
            report = await service.generate_daily_report()

        # Format message
        message = format_report_message(report)

        # Get admin bot
        if not settings.telegram_admin_bot_token:
            logger.warning("admin_bot_token_not_configured")
            return False

        if not settings.admin_user_ids:
            logger.warning("admin_user_ids_not_configured")
            return False

        bot = Bot(token=settings.telegram_admin_bot_token)

        # Send to all admins
        success = True
        for admin_id in settings.admin_user_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=message,
                )
                logger.info("daily_report_sent", admin_id=admin_id)
            except Exception as e:
                logger.error(
                    "daily_report_send_failed",
                    admin_id=admin_id,
                    error=str(e)
                )
                success = False

        await bot.session.close()

        logger.info("daily_business_report_completed", success=success)
        return success

    except Exception as e:
        logger.error("daily_report_generation_failed", error=str(e))
        return False
