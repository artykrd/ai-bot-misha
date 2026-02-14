"""
Broadcast service for managing broadcast messages and statistics.
"""
from datetime import datetime, timedelta
from typing import Optional, Union

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message, BufferedInputFile
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.database.models.broadcast import BroadcastMessage, BroadcastClick
from app.database.models.user import User
from app.database.models.subscription import Subscription

logger = get_logger(__name__)


async def send_broadcast_message(
    bot: Bot,
    chat_id: int,
    text: str,
    photo: Optional[Union[str, BufferedInputFile]] = None,
    keyboard: Optional[InlineKeyboardMarkup] = None,
) -> Optional[Message]:
    """
    Unified method for sending broadcast messages to users.

    Ensures photo, caption, and reply_markup are never lost
    by using a single send call with all attachments.

    Args:
        bot: Bot instance to send through
        chat_id: Telegram user chat ID
        text: Message text (used as caption when photo is present)
        photo: Telegram file_id, BufferedInputFile, or None
        keyboard: InlineKeyboardMarkup to attach (optional)

    Returns:
        Sent Message object (useful to extract file_id after first upload)
    """
    if photo:
        return await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=text,
            reply_markup=keyboard,
            parse_mode=None,
        )
    else:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=None,
        )


async def create_broadcast_message(
    session: AsyncSession,
    admin_id: Optional[int],
    text: str,
    image_file_id: Optional[str],
    buttons: list[dict],
    filter_type: str,
) -> BroadcastMessage:
    """
    Create a new broadcast message record.

    Args:
        session: Database session
        admin_id: Internal user ID (from users.id) or None.
                  Caller must resolve telegram_id to internal ID before calling.
        text: Message text
        image_file_id: Telegram file_id for photo (optional)
        buttons: List of button dicts with 'text' and 'callback_data'
        filter_type: Recipient filter (all/subscribed/free)

    Returns:
        Created BroadcastMessage instance
    """
    broadcast = BroadcastMessage(
        admin_id=admin_id,
        text=text,
        image_file_id=image_file_id,
        buttons=buttons,
        filter_type=filter_type,
        sent_count=0,
        error_count=0,
    )

    session.add(broadcast)
    await session.commit()
    await session.refresh(broadcast)

    return broadcast


async def update_broadcast_stats(
    session: AsyncSession,
    broadcast_id: int,
    sent_count: int,
    error_count: int,
) -> None:
    """
    Update broadcast delivery statistics.

    Args:
        session: Database session
        broadcast_id: Broadcast message ID
        sent_count: Number of successfully sent messages
        error_count: Number of failed deliveries
    """
    result = await session.execute(
        select(BroadcastMessage).where(BroadcastMessage.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()

    if broadcast:
        broadcast.sent_count = sent_count
        broadcast.error_count = error_count
        await session.commit()


async def get_recipients_count(session: AsyncSession, filter_type: str) -> int:
    """
    Get count of users matching filter.

    Args:
        session: Database session
        filter_type: Filter type (all/subscribed/free)

    Returns:
        Count of matching users
    """
    if filter_type == "all":
        result = await session.execute(
            select(func.count(User.id)).where(User.is_banned == False)
        )
    elif filter_type == "subscribed":
        result = await session.execute(
            select(func.count(User.id))
            .join(Subscription, User.id == Subscription.user_id)
            .where(
                and_(
                    User.is_banned == False,
                    Subscription.is_active == True,
                    Subscription.end_date > datetime.utcnow()
                )
            )
        )
    else:  # free
        subquery = select(Subscription.user_id).where(
            and_(
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        result = await session.execute(
            select(func.count(User.id)).where(
                and_(
                    User.is_banned == False,
                    User.id.notin_(subquery)
                )
            )
        )

    return result.scalar() or 0


async def get_recipients(session: AsyncSession, filter_type: str) -> list[User]:
    """
    Get list of users matching filter.

    Args:
        session: Database session
        filter_type: Filter type (all/subscribed/free)

    Returns:
        List of User instances
    """
    if filter_type == "all":
        result = await session.execute(
            select(User).where(User.is_banned == False)
        )
    elif filter_type == "subscribed":
        result = await session.execute(
            select(User)
            .join(Subscription, User.id == Subscription.user_id)
            .where(
                and_(
                    User.is_banned == False,
                    Subscription.is_active == True,
                    Subscription.end_date > datetime.utcnow()
                )
            )
        )
    else:  # free
        subquery = select(Subscription.user_id).where(
            and_(
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow()
            )
        )
        result = await session.execute(
            select(User).where(
                and_(
                    User.is_banned == False,
                    User.id.notin_(subquery)
                )
            )
        )

    return list(result.scalars().all())


async def record_broadcast_click(
    session: AsyncSession,
    broadcast_id: int,
    user_id: int,
    button_index: int,
    button_text: str,
    button_callback_data: str,
) -> BroadcastClick:
    """
    Record a user click on broadcast button.

    Args:
        session: Database session
        broadcast_id: Broadcast message ID
        user_id: User ID who clicked
        button_index: Index of button in buttons array
        button_text: Button text
        button_callback_data: Button callback_data

    Returns:
        Created BroadcastClick instance
    """
    click = BroadcastClick(
        broadcast_id=broadcast_id,
        user_id=user_id,
        button_index=button_index,
        button_text=button_text,
        button_callback_data=button_callback_data,
    )

    session.add(click)
    await session.commit()
    await session.refresh(click)

    return click


async def get_broadcast_by_callback(
    session: AsyncSession,
    callback_data: str
) -> Optional[BroadcastMessage]:
    """
    Find broadcast message containing button with given callback_data.

    Args:
        session: Database session
        callback_data: Callback data to search for

    Returns:
        BroadcastMessage if found, None otherwise
    """
    # Get recent broadcasts (last 30 days)
    recent_date = datetime.utcnow() - timedelta(days=30)

    result = await session.execute(
        select(BroadcastMessage).where(
            BroadcastMessage.created_at > recent_date
        )
    )
    broadcasts = result.scalars().all()

    # Search for callback_data in buttons
    for broadcast in broadcasts:
        if broadcast.buttons:
            for button in broadcast.buttons:
                if button.get("callback_data") == callback_data:
                    return broadcast

    return None


async def get_broadcast_statistics(
    session: AsyncSession,
    broadcast_id: int
) -> dict:
    """
    Get detailed statistics for a broadcast.

    Args:
        session: Database session
        broadcast_id: Broadcast message ID

    Returns:
        Dict with statistics including click counts per button
    """
    # Get broadcast
    result = await session.execute(
        select(BroadcastMessage).where(BroadcastMessage.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()

    if not broadcast:
        return {}

    # Get total clicks
    result = await session.execute(
        select(func.count(BroadcastClick.id)).where(
            BroadcastClick.broadcast_id == broadcast_id
        )
    )
    total_clicks = result.scalar() or 0

    # Get unique users who clicked
    result = await session.execute(
        select(func.count(func.distinct(BroadcastClick.user_id))).where(
            BroadcastClick.broadcast_id == broadcast_id
        )
    )
    unique_users = result.scalar() or 0

    # Get clicks per button
    button_stats = []
    if broadcast.buttons:
        for idx, button in enumerate(broadcast.buttons):
            # Total clicks for this button
            result = await session.execute(
                select(func.count(BroadcastClick.id)).where(
                    and_(
                        BroadcastClick.broadcast_id == broadcast_id,
                        BroadcastClick.button_index == idx
                    )
                )
            )
            button_clicks = result.scalar() or 0

            # Unique users for this button
            result = await session.execute(
                select(func.count(func.distinct(BroadcastClick.user_id))).where(
                    and_(
                        BroadcastClick.broadcast_id == broadcast_id,
                        BroadcastClick.button_index == idx
                    )
                )
            )
            button_unique = result.scalar() or 0

            button_stats.append({
                "index": idx,
                "text": button.get("text", ""),
                "clicks": button_clicks,
                "unique_users": button_unique,
            })

    # Get clicks over time (first hour, first day, total)
    now = datetime.utcnow()
    first_hour = broadcast.created_at + timedelta(hours=1)
    first_day = broadcast.created_at + timedelta(days=1)

    result = await session.execute(
        select(func.count(BroadcastClick.id)).where(
            and_(
                BroadcastClick.broadcast_id == broadcast_id,
                BroadcastClick.created_at <= first_hour
            )
        )
    )
    clicks_first_hour = result.scalar() or 0

    result = await session.execute(
        select(func.count(BroadcastClick.id)).where(
            and_(
                BroadcastClick.broadcast_id == broadcast_id,
                BroadcastClick.created_at <= first_day
            )
        )
    )
    clicks_first_day = result.scalar() or 0

    return {
        "broadcast": broadcast,
        "total_clicks": total_clicks,
        "unique_users": unique_users,
        "button_stats": button_stats,
        "timeline": {
            "first_hour": clicks_first_hour,
            "first_day": clicks_first_day,
            "total": total_clicks,
        }
    }


async def get_recent_broadcasts(
    session: AsyncSession,
    page: int = 0,
    page_size: int = 10
) -> tuple[list[BroadcastMessage], int]:
    """
    Get recent broadcasts with pagination.

    Args:
        session: Database session
        page: Page number (0-indexed)
        page_size: Items per page

    Returns:
        Tuple of (list of broadcasts, total count)
    """
    # Get total count
    result = await session.execute(
        select(func.count(BroadcastMessage.id))
    )
    total_count = result.scalar() or 0

    # Get page of broadcasts
    result = await session.execute(
        select(BroadcastMessage)
        .order_by(BroadcastMessage.created_at.desc())
        .limit(page_size)
        .offset(page * page_size)
    )
    broadcasts = list(result.scalars().all())

    return broadcasts, total_count
