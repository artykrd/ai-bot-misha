"""
Channel subscription bonus handler for user bot.
Handles the "check subscription" button callback from broadcast messages.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="channel_bonus")


@router.callback_query(F.data.startswith("bot.check_channel_sub:"))
async def check_channel_subscription(callback: CallbackQuery, user: User):
    """
    Handle user clicking 'Check subscription' button.
    Verifies channel membership and awards bonus tokens.
    """
    from app.database.database import async_session_maker
    from app.services.channel_bonus import ChannelBonusService
    from app.services.subscription.subscription_service import SubscriptionService
    from app.bot.bot_instance import bot

    bonus_id_str = callback.data.split(":")[-1]
    try:
        bonus_id = int(bonus_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: некорректные данные.", show_alert=True)
        return

    async with async_session_maker() as session:
        service = ChannelBonusService(session)
        bonus = await service.get_bonus_by_id(bonus_id)

        if not bonus or not bonus.is_active:
            await callback.answer(
                "❌ Этот бонус больше не активен.",
                show_alert=True,
            )
            return

        # Check if already claimed
        if await service.has_claimed(user.id, bonus_id):
            await callback.answer(
                "ℹ️ Вы уже получили этот бонус!",
                show_alert=True,
            )
            return

        # Check if user is subscribed to the channel
        is_member = await ChannelBonusService.check_channel_membership(
            bot=bot,
            user_telegram_id=user.telegram_id,
            channel_id=bonus.channel_id,
        )

        if not is_member:
            ch_name = bonus.channel_title or "канал"
            if bonus.channel_username:
                ch_name = f"@{bonus.channel_username}"
            await callback.answer(
                f"❌ Вы не подписаны на {ch_name}.\n\n"
                f"Подпишитесь на канал и нажмите кнопку ещё раз!",
                show_alert=True,
            )
            return

        # Award the bonus
        tokens_awarded = await service.claim_bonus(
            user_id=user.id,
            bonus_id=bonus_id,
        )

        if tokens_awarded is None:
            await callback.answer(
                "❌ Не удалось начислить бонус. Попробуйте позже.",
                show_alert=True,
            )
            return

    # Success! Show the welcome message
    welcome = bonus.welcome_message or (
        f"🎉 Поздравляем! Вам начислено {tokens_awarded:,} бонусных токенов "
        f"за подписку на канал!"
    )

    await callback.answer(
        f"🎉 +{tokens_awarded:,} токенов!",
        show_alert=True,
    )

    # Also send a message so user can see their balance
    from app.services.subscription.subscription_service import SubscriptionService as SubSvc

    async with async_session_maker() as session:
        sub_service = SubSvc(session)
        total_tokens = await sub_service.get_available_tokens(user.id)

    try:
        await callback.message.answer(
            f"{welcome}\n\n"
            f"💰 Ваш текущий баланс: {total_tokens:,} токенов"
        )
    except Exception as e:
        logger.error("channel_bonus_welcome_message_error", error=str(e))

    logger.info(
        "channel_bonus_awarded_to_user",
        user_id=user.id,
        telegram_id=user.telegram_id,
        bonus_id=bonus_id,
        tokens=tokens_awarded,
    )
