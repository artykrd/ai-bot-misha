#!/usr/bin/env python3
# coding: utf-8
"""
Common handlers for not implemented features.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

from app.bot.keyboards.inline import back_to_main_keyboard, main_menu_keyboard, subscription_keyboard

router = Router(name="common")


# Command handlers for menu commands
@router.message(Command("shop"))
async def cmd_shop(message: Message):
    """Shop command - show subscription."""
    text = """💎 **Оформить подписку**

🤩 **Наш бот предоставляет вам лучший сервис** без каких либо ограничений и продолжает это делать ежедневно 24/7. **Подписка позволит вам получить больше возможностей**, чем если использовать бот бесплатно.

**Выберите подходящий тариф:**"""

    await message.answer(
        text,
        reply_markup=subscription_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(Command("models"))
async def cmd_models(message: Message):
    """Models command - show model selection."""
    from app.bot.handlers.text_ai import select_ai_model
    text = """🤖 **Выбор AI модели**

Выберите модель для диалога:

**GPT-4 Omni** - самая продвинутая модель OpenAI (1000 токенов)
**GPT-4 Mini** - быстрая и доступная модель (250 токенов)
**Claude 3.5** - модель от Anthropic (1200 токенов)
**Gemini Pro** - модель от Google (900 токенов)
**DeepSeek** - отличная альтернатива (800 токенов)"""

    from app.bot.keyboards.inline import ai_models_keyboard
    await message.answer(text, reply_markup=ai_models_keyboard(), parse_mode=ParseMode.MARKDOWN)


@router.message(Command("faq"))
@router.callback_query(F.data == "help")
async def cmd_faq(event):
    """FAQ/Help command."""
    is_callback = isinstance(event, CallbackQuery)

    text = """🆘 <b>Помощь</b>

<b>Как пользоваться ботом:</b>
1️⃣ Выберите AI модель через /models
2️⃣ Отправьте текстовый запрос
3️⃣ Получите ответ от AI

<b>Токены:</b>
• Каждый запрос стоит определенное количество токенов
• Пополнить баланс: /shop
• Посмотреть баланс: /profile

<b>Поддержка:</b>
Если возникли вопросы, напишите @support"""

    if is_callback:
        await event.message.edit_text(text, reply_markup=back_to_main_keyboard(), parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)


@router.message(Command("ref"))
async def cmd_ref(message: Message):
    """Referral command."""
    text = """🤝🏼 <b>Пригласи друга</b>

⚠️ Функционал в разработке

Скоро вы сможете:
• Получать бонусы за приглашенных друзей
• Зарабатывать на рефералах
• Получать процент от покупок друзей"""
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)


@router.message(Command("promocode"))
async def cmd_promocode(message: Message):
    """Promocode command."""
    text = """🔢 <b>Активировать промокод</b>

⚠️ Функционал в разработке

Отправьте промокод для активации."""
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode=ParseMode.HTML)


# Media generation commands
@router.message(Command("sora"))
async def cmd_sora(message: Message):
    """Sora 2 command."""
    await message.answer(
        "🎬 <b>Sora 2</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 50,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("veo"))
async def cmd_veo(message: Message):
    """Veo 3.1 command."""
    await message.answer(
        "🎬 <b>Veo 3.1</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 50,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("nano"))
async def cmd_nano(message: Message):
    """Nano Banana command."""
    await message.answer(
        "🍌 <b>Nano Banana</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 8,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("suno"))
async def cmd_suno(message: Message):
    """Suno command."""
    await message.answer(
        "🎵 <b>Suno - создание музыки</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 20,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("image"))
async def cmd_image(message: Message):
    """GPT Image command."""
    await message.answer(
        "🖼 <b>GPT Image 1</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 8,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("mj"))
async def cmd_mj(message: Message):
    """Midjourney command."""
    await message.answer(
        "🎨 <b>Midjourney</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 20,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("dalle"))
async def cmd_dalle(message: Message):
    """DALLE 3 command."""
    await message.answer(
        "🎨 <b>DALL·E 3</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 10,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("recraft"))
async def cmd_recraft(message: Message):
    """Recraft command."""
    await message.answer(
        "🎨 <b>Recraft</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 15,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("faceswap"))
async def cmd_faceswap(message: Message):
    """Faceswap command."""
    await message.answer(
        "👤 <b>Замена лица на фото</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 8,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("instruments"))
async def cmd_instruments(message: Message):
    """Photo instruments command."""
    await message.answer(
        "✂️ <b>Работа с фото</b>\n\n⚠️ Функционал в разработке\n\nДоступные инструменты:\n• Улучшение фото\n• Удаление фона\n• Замена фона\n• Векторизация",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("whisper"))
async def cmd_whisper(message: Message):
    """Whisper command."""
    await message.answer(
        "🎙 <b>Расшифровка голоса</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 1,000 токенов за минуту",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("mvideo"))
async def cmd_mvideo(message: Message):
    """Midjourney Video command."""
    await message.answer(
        "🎬 <b>Midjourney Video</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 30,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("luma"))
async def cmd_luma(message: Message):
    """Luma Dream Machine command."""
    await message.answer(
        "🎬 <b>Luma Dream Machine</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 30,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("kling"))
async def cmd_kling(message: Message):
    """Kling command."""
    await message.answer(
        "🎬 <b>Kling</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 30,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("hailuo"))
async def cmd_hailuo(message: Message):
    """Hailuo command."""
    await message.answer(
        "🎬 <b>Hailuo</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 30,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


# Callback handlers
@router.callback_query(F.data == "my_payments")
async def show_my_payments(callback: CallbackQuery):
    """Show user payments."""
    await callback.message.edit_text(
        "💳 <b>Мои платежи</b>\n\n⚠️ Функционал в разработке\n\nЗдесь будет история ваших платежей",
        reply_markup=back_to_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data == "dialogs")
async def show_dialogs(callback: CallbackQuery):
    """Show dialogs (not implemented)."""
    await callback.message.edit_text(
        "💬 **Диалоги**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "create_photo")
async def create_photo(callback: CallbackQuery):
    """Create photo (not implemented)."""
    await callback.message.edit_text(
        "🌄 **Создание фото**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "create_video")
async def create_video(callback: CallbackQuery):
    """Create video (not implemented)."""
    await callback.message.edit_text(
        "🎞 **Создание видео**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "photo_tools")
async def photo_tools(callback: CallbackQuery):
    """Photo tools (not implemented)."""
    await callback.message.edit_text(
        "✂️ **Работа с фото**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "audio_tools")
async def audio_tools(callback: CallbackQuery):
    """Audio tools (not implemented)."""
    await callback.message.edit_text(
        "🎙 **Работа с аудио**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "referral")
async def referral(callback: CallbackQuery):
    """Referral program (not implemented)."""
    await callback.message.edit_text(
        "🤝🏼 **Партнерство**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()
