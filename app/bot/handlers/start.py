#!/usr/bin/env python3
# coding: utf-8
"""
Start command handler.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.inline import main_menu_keyboard
from app.bot.keyboards.reply import main_menu_reply_keyboard
from app.database.models.user import User
from app.bot.states.media import clear_state_preserve_settings

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, state: FSMContext):
    """Handle /start command with optional referral code or unlimited invite."""
    from app.bot.handlers.dialog_context import clear_active_dialog
    from app.database.database import async_session_maker
    from app.database.models.referral import Referral
    from app.database.models.unlimited_invite import UnlimitedInviteLink, UnlimitedInviteUse
    from app.database.models.subscription import Subscription
    from sqlalchemy import select
    from datetime import datetime, timedelta, timezone

    await clear_state_preserve_settings(state)
    await clear_active_dialog(user.telegram_id)

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
                            f"🎉 Поздравляем!\n\n"
                            f"Вы получили безлимитный доступ на {invite_link.duration_days} дней!\n\n"
                            f"✨ У вас неограниченные токены до {expires_at.strftime('%d.%m.%Y %H:%M')} UTC\n\n"
                            f"Используйте бота без ограничений!",
                            parse_mode=None
                        )
                    else:
                        await message.answer(
                            "ℹ️ Вы уже использовали безлимитную пригласительную ссылку ранее."
                        )

        # Regular referral code
        elif args.startswith("ref"):
            try:
                referrer_telegram_id = int(args[3:])  # Extract ID from "ref123456789"

                # Use ReferralService to handle referral logic
                async with async_session_maker() as session:
                    from app.services.referral import ReferralService

                    referral_service = ReferralService(session)

                    # Find referrer
                    referrer_result = await session.execute(
                        select(User).where(User.telegram_id == referrer_telegram_id)
                    )
                    referrer = referrer_result.scalar_one_or_none()

                    if referrer and referrer.id != user.id:
                        # Create referral relationship
                        referral = await referral_service.create_referral(
                            referrer_id=referrer.id,
                            referred_id=user.id,
                            referral_code=args,
                            referral_type="user"
                        )

                        if referral:
                            # Give signup bonus: inviter gets 100 tokens
                            # Invited user already gets 5000 welcome tokens via auth middleware
                            bonus_given = await referral_service.give_signup_bonus(
                                referrer_id=referrer.id,
                                referred_id=user.id,
                                referrer_bonus=100,
                            )

                            if bonus_given:
                                await message.answer(
                                    f"🎉 Вы были приглашены пользователем {referrer.full_name}!\n"
                                    f"Вам начислено 5 000 приветственных токенов!",
                                    parse_mode=None
                                )
                            else:
                                # Referral created but bonus failed
                                await message.answer(
                                    f"🎉 Вы были приглашены пользователем {referrer.full_name}!\n"
                                    f"⚠️ Возникла проблема с начислением бонуса. Свяжитесь с поддержкой.",
                                    parse_mode=None
                                )
            except (ValueError, IndexError):
                pass  # Invalid referral code format

    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService

    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_available_tokens(user.id)

    welcome_text = f"""Привет! У тебя на балансе {total_tokens:,} токенов — используй их для запросов к нейросетям.

🧠 Языковые модели:
– ChatGPT: работает с текстом, голосом, может принимать до 10 картинок и документы любого формата;
– Claude и Gemini: отлично работают с текстом и документами;
– DeepSeek: отличная альтернатива для сложных задач;
– Sonar: модели с доступом к поиску в интернете.

🎨 Создание изображений:
– Midjourney, DALL·E, Stable Diffusion, Recraft — генерация изображений по описанию;
– Nano Banana — создаёт фото по промпту и вашим изображениям;
– GPT Image — генерация изображений от OpenAI.

🎬 Создание видео:
– Sora 2, Veo 3.1 — новейшие модели видеогенерации;
– Midjourney Video, Hailuo, Luma, Kling — создание видео по описанию.

🎵 Работа с аудио:
– Suno — создание музыки и песен;
– Whisper — расшифровка голосовых сообщений;
– TTS — озвучка текста."""

    await message.answer(
        welcome_text,
        reply_markup=main_menu_reply_keyboard()
    )


@router.callback_query(F.data.in_(["main_menu", "bot.back"]))
async def show_main_menu(callback: CallbackQuery, user: User, state: FSMContext):
    """Show main menu. Handles both legacy 'main_menu' and new 'bot.back' callbacks."""
    from app.database.database import async_session_maker
    from app.services.subscription.subscription_service import SubscriptionService
    from app.bot.handlers.dialog_context import clear_active_dialog

    await clear_state_preserve_settings(state)
    await clear_active_dialog(user.telegram_id)
    async with async_session_maker() as session:
        sub_service = SubscriptionService(session)
        total_tokens = await sub_service.get_available_tokens(user.id)

    welcome_text = f"""Привет! У тебя на балансе {total_tokens:,} токенов — используй их для запросов к нейросетям.

🧠 Языковые модели:
– ChatGPT: работает с текстом, голосом, может принимать до 10 картинок и документы любого формата;
– Claude и Gemini: отлично работают с текстом и документами;
– DeepSeek: отличная альтернатива для сложных задач;
– Sonar: модели с доступом к поиску в интернете.

🎨 Создание изображений:
– Midjourney, DALL·E, Stable Diffusion, Recraft — генерация изображений по описанию;
– Nano Banana — создаёт фото по промпту и вашим изображениям;
– GPT Image — генерация изображений от OpenAI.

🎬 Создание видео:
– Sora 2, Veo 3.1 — новейшие модели видеогенерации;
– Midjourney Video, Hailuo, Luma, Kling — создание видео по описанию.

🎵 Работа с аудио:
– Suno — создание музыки и песен;
– Whisper — расшифровка голосовых сообщений;
– TTS — озвучка текста."""

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await callback.message.answer(
        welcome_text,
        reply_markup=main_menu_reply_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.menu")
async def show_full_menu(callback: CallbackQuery, user: User, state: FSMContext):
    """Show full menu."""
    from app.bot.handlers.dialog_context import clear_active_dialog

    await clear_state_preserve_settings(state)
    await clear_active_dialog(user.telegram_id)
    text = "Меню"
    if callback.message.photo:
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass
        await callback.message.answer(text, reply_markup=main_menu_keyboard())
        await callback.answer()
        return
    try:
        await callback.message.edit_text(text, reply_markup=main_menu_keyboard())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(F.text == "Меню")
async def show_full_menu_message(message: Message, user: User, state: FSMContext):
    """Show full menu by reply button."""
    from app.bot.handlers.dialog_context import clear_active_dialog

    await clear_state_preserve_settings(state)
    await clear_active_dialog(user.telegram_id)
    await message.answer("Меню", reply_markup=main_menu_keyboard())
