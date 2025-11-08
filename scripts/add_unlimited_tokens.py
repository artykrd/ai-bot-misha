"""
Script to add unlimited test subscription to user.

Usage:
    python scripts/add_unlimited_tokens.py [telegram_id]

If telegram_id is not provided, will add to the first user in database.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from app.database.database import async_session_maker
from app.database.models.user import User
from app.database.models.subscription import Subscription


async def add_unlimited_subscription(telegram_id: int = None):
    """Add unlimited test subscription to user."""

    async with async_session_maker() as session:
        # Find user
        if telegram_id:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                print(f"❌ User with telegram_id {telegram_id} not found!")
                return
        else:
            # Get first user
            result = await session.execute(
                select(User).order_by(User.created_at.desc()).limit(1)
            )
            user = result.scalar_one_or_none()
            if not user:
                print("❌ No users found in database!")
                return

        print(f"Found user: {user.full_name} (telegram_id: {user.telegram_id})")

        # Check existing subscriptions
        existing_subs = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.is_active == True
            )
        )
        active_subs = existing_subs.scalars().all()

        if active_subs:
            print(f"\n⚠️  User already has {len(active_subs)} active subscription(s):")
            for sub in active_subs:
                remaining = sub.tokens_amount - sub.tokens_used
                print(f"  - {sub.subscription_type}: {remaining:,} tokens remaining")

            response = input("\nDeactivate existing subscriptions and add new one? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return

            # Deactivate existing subscriptions
            for sub in active_subs:
                sub.is_active = False
            await session.commit()
            print("✅ Deactivated existing subscriptions")

        # Create new unlimited subscription
        new_subscription = Subscription(
            user_id=user.id,
            subscription_type="unlimited_test",
            tokens_amount=9999999,
            tokens_used=0,
            price=0.00,
            is_active=True,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365)
        )

        session.add(new_subscription)
        await session.commit()
        await session.refresh(new_subscription)

        print(f"\n✅ Successfully added unlimited test subscription!")
        print(f"   User: {user.full_name} (telegram_id: {user.telegram_id})")
        print(f"   Tokens: {new_subscription.tokens_amount:,}")
        print(f"   Expires: {new_subscription.expires_at.strftime('%Y-%m-%d')}")
        print(f"\n🚀 User can now test the bot unlimited times!")


async def main():
    """Main function."""
    telegram_id = None

    if len(sys.argv) > 1:
        try:
            telegram_id = int(sys.argv[1])
            print(f"Adding subscription to user with telegram_id: {telegram_id}")
        except ValueError:
            print(f"❌ Invalid telegram_id: {sys.argv[1]}")
            print("Usage: python scripts/add_unlimited_tokens.py [telegram_id]")
            return

    await add_unlimited_subscription(telegram_id)


if __name__ == "__main__":
    asyncio.run(main())
