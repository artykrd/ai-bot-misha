#!/usr/bin/env python3
# coding: utf-8
"""
Start command handler.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.inline import main_menu_keyboard
from app.database.models.user import User

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: User):
    """Handle /start command with optional referral code or unlimited invite."""
    from app.database.database import async_session_maker
    from app.database.models.referral import Referral
    from app.database.models.unlimited_invite import UnlimitedInviteLink, UnlimitedInviteUse
    from app.database.models.subscription import Subscription
    from sqlalchemy import select
    from datetime import datetime, timedelta, timezone

    # Check for referral code or unlimited invite in command args
    if message.text and len(message.text.split()) > 1:
        args = message.text.split()[1]  # Get argument after /start

        # Check if it's an unlimited invite link
        if args.startswith("unlimited_"):
            async with async_session_maker() as session:
                # Find the invite link
                result = await session.execute(
                    select(UnlimitedInviteLink).where(
                        UnlimitedInviteLink.invite_code == args
                    )
                )
                invite_link = result.scalar_one_or_none()

                if invite_link and invite_link.is_valid:
                    # Check if user already used this type of link
                    existing_use = await session.execute(
                        select(UnlimitedInviteUse).where(
                            UnlimitedInviteUse.user_id == user.id
                        )
                    )
                    has_used = existing_use.scalar_one_or_none()

                    if not has_used:
                        # Create unlimited subscription for the user
                        from app.services.subscription.subscription_service import SubscriptionService

                        sub_service = SubscriptionService(session)

                        # Create subscription with unlimited tokens for specified duration
                        started_at = datetime.now(timezone.utc)
                        expires_at = started_at + timedelta(days=invite_link.duration_days)

                        subscription = Subscription(
                            user_id=user.id,
                            subscription_type=f"unlimited_{invite_link.duration_days}days",
                            tokens_amount=999999999,  # Virtually unlimited
                            tokens_used=0,
                            price=0.0,
                            is_active=True,
                            started_at=started_at,
                            expires_at=expires_at
                        )

                        session.add(subscription)
                        await session.flush()  # Get subscription ID

                        # Track the usage
                        invite_use = UnlimitedInviteUse(
                            invite_link_id=invite_link.id,
                            user_id=user.id,
                            subscription_id=subscription.id
                        )
                        session.add(invite_use)

                        # Increment usage counter
                        invite_link.current_uses += 1

                        await session.commit()

                        await message.answer(
                            f"🎉 **Поздравляем!**\n\n"
                            f"Вы получили **безлимитный доступ** на **{invite_link.duration_days} дней**!\n\n"
                            f"✨ У вас неограниченные токены до {expires_at.strftime('%d.%m.%Y %H:%M')} UTC\n\n"
                            f"Используйте бота без ограничений!"
                        )
                    else:
                        await message.answer(
                            "ℹ️ Вы уже использовали безлимитную пригласительную ссылку ранее."
                        )

        # Regular referral code
        elif args.startswith("ref"):
            try:
                referrer_telegram_id = int(args[3:])  # Extract ID from "ref123456789"

                # Check if user already has a referral
                async with async_session_maker() as session:
                    # Find referrer
                    referrer_result = await session.execute(
                        select(User).where(User.telegram_id == referrer_telegram_id)
                    )
                    referrer = referrer_result.scalar_one_or_none()

                    # Check if already has referral
                    existing_referral = await session.execute(
                        select(Referral).where(Referral.referred_id == user.id)
                    )
                    has_referral = existing_referral.scalar_one_or_none()

                    if referrer and not has_referral and referrer.id != user.id:
                        # Create referral relationship
                        new_referral = Referral(
                            referrer_id=referrer.id,
                            referred_id=user.id,
                            referral_code=args,
                            referral_type="user",
                            tokens_earned=0,
                            money_earned=0,
                            is_active=True
                        )
                        session.add(new_referral)
                        await session.commit()

                        await message.answer(
                            f"🎉 Вы были приглашены пользователем {referrer.full_name}!\n"
                            f"Вам начислено 100 бонусных токенов!"
                        )
            except (ValueError, IndexError):
                pass  # Invalid referral code format

    total_tokens = user.get_total_tokens()

    welcome_text = f"""👋🏻 **Привет!** У тебя на балансе **{total_tokens:,} токенов** – используй их для запросов к нейросетям.

💬 **Языковые модели:**
– **ChatGPT:** работает с текстом, голосом, может принимать до 10 картинок и анализировать их;
– **Claude, Gemini, DeepSeek** и другие модели для диалога.

🌄 **Генерация изображений:**
– **Nano Banana, Midjourney, DALL-E 3, Stable Diffusion** и другие.

🎞 **Генерация видео:**
– **Sora, Veo, Luma, Kling** и другие.

🎙 **Аудио:**
– **Suno** для создания музыки;
– **Whisper** для распознавания речи;
– **TTS** для озвучки текста.

✂️ **Инструменты:**
– Улучшение качества, удаление фона, векторизация и многое другое.

Выбери нужный раздел в меню ниже! 👇"""

    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )


@router.callback_query(F.data.in_(["main_menu", "bot.back"]))
async def show_main_menu(callback: CallbackQuery, user: User):
    """Show main menu. Handles both legacy 'main_menu' and new 'bot.back' callbacks."""
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_user_total_tokens(user.id)

    welcome_text = f"""👋🏻 **Привет!** У тебя на балансе **{total_tokens:,} токенов** ** **– используй их для запросов к нейросетям.

💬 **Языковые модели:**
– **ChatGPT:** работает с текстом, голосом, может принимать до 10 картинок и документы любого формата;
– **Claude** и **Gemini:** отлично работают с текстом и документами;
– **DeepSeek:** отличная альтернатива для сложных задач;
– **Sonar:** модели с доступом к поиску в интернете.

🌄 **Создание изображений:**
– **Midjourney, DALL·E, Stable Diffusion, Recraft** – генерация изображений по описанию;
– **Nano Banana** – создаёт фото по промпту и вашим изображениям;
– **GPT Image** – генерация от OpenAI.

🎬 **Создание видео:**
– **Sora 2, Veo 3.1** – новейшие модели видеогенерации;
– **Midjourney Video, Hailuo, Luma, Kling** – создание видео по описанию.

🎙 **Работа с аудио:**
– **Suno** – создание музыки и песен;
– **Whisper** – расшифровка голосовых сообщений;
– **TTS** – озвучка текста."""

    # Check if message has photo (e.g., after image generation)
    # If so, delete and send new message instead of editing
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            welcome_text,
            reply_markup=main_menu_keyboard()
        )
    await callback.answer()
