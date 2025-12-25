#!/usr/bin/env python3
# coding: utf-8
"""
Common handlers for not implemented features.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

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
**Claude 4** - модель от Anthropic (1200 токенов)
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
async def cmd_sora(message: Message, state):
    """Sora 2 command - directly open Sora interface."""
    from app.bot.keyboards.inline import back_to_main_keyboard
    from app.bot.handlers.media_handler import MediaState

    text = (
        "**Sora 2 - Video Generation**\n\n"
        "Sora 2 может создавать реалистичные видео длительностью до 20 секунд по вашему описанию.\n\n"
        "💰 **Стоимость:** ~15,000 токенов за видео\n\n"
        "✏️ **Отправьте текстовое описание видео, которое вы хотите создать**"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    # Clear old data when starting fresh session
    await state.update_data(service="sora", image_path=None, photo_caption_prompt=None)

    await message.answer(text, reply_markup=back_to_main_keyboard())



@router.message(Command("veo"))
async def cmd_veo(message: Message, state):
    """Veo 3.1 command - directly open Veo interface."""
    from app.bot.keyboards.inline import back_to_main_keyboard
    from app.bot.handlers.media_handler import MediaState

    text = (
        "🌊 **Veo 3.1 - Video Generation**\n\n"
        "Google Veo создаёт реалистичные HD видео по вашему описанию.\n\n"
        "📊 **Параметры:**\n"
        "• Длительность: 8 секунд\n"
        "• Разрешение: 720p\n"
        "• Форматы: 16:9, 9:16, 1:1, 4:3, 3:4\n\n"
        "💰 **Стоимость:** ~15,000 токенов за видео\n\n"
        "✏️ **Отправьте описание видео**\n"
        "_Чем детальнее описание, тем лучше результат!_\n\n"
        "**Примеры:**\n"
        "• \"Золотой ретривер играет в поле подсолнухов\"\n"
        "• \"Чашка кофе на деревянном столе, утренний свет\"\n"
        "• \"Ночной город с потоками света машин\""
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="veo")

    await message.answer(text, reply_markup=back_to_main_keyboard(), parse_mode=ParseMode.MARKDOWN)


@router.message(Command("nano"))
async def cmd_nano(message: Message, state):
    """Nano Banana command - directly open Nano Banana interface."""
    from app.bot.keyboards.inline import nano_banana_keyboard
    from app.bot.handlers.media_handler import MediaState, cleanup_temp_images

    # Clean up any old images from previous sessions
    await cleanup_temp_images(state)

    text = """🍌 **Nano Banana · твори и экспериментируй**

📖 **Создавайте:**
– Создает фотографии по промпту и по вашим изображениям;
– Она отлично наследует исходное фото и может работать с ним. Попросите её, например, "перенести этот стиль на новое изображение".

**Стоимость:** 3,000 токенов за запрос

✏️ **Отправьте текстовый запрос для генерации изображения**"""

    # Set FSM state to wait for prompt
    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="nano_banana", reference_image_path=None, photo_caption_prompt=None)

    await message.answer(text, reply_markup=nano_banana_keyboard(), parse_mode=ParseMode.MARKDOWN)


@router.message(Command("suno"))
async def cmd_suno(message: Message):
    """Suno command - redirect to audio instruments menu."""
    from app.bot.keyboards.inline import audio_tools_keyboard

    text = """🎙 **Работа с аудио**

__ℹ️ Выберите нейросеть для работы с аудио по кнопке ниже. После выбора – можете сразу отправлять запрос.__"""

    await message.answer(
        text,
        reply_markup=audio_tools_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(Command("image"))
async def cmd_image(message: Message, state: FSMContext):
    """GPT Image command - DALL-E image generation."""
    from app.bot.states import MediaState
    from app.bot.handlers.media_handler import cleanup_temp_images

    # Clean up any old images from previous sessions
    await cleanup_temp_images(state)

    text = (
        "🖼 **GPT Image 1 (DALL-E 3)**\n\n"
        "Создайте уникальные изображения по текстовому описанию.\n\n"
        "💰 **Стоимость:** 5,300 токенов за запрос\n\n"
        "✏️ **Отправьте описание изображения**"
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="dalle", reference_image_path=None, photo_caption_prompt=None)

    await message.answer(text, reply_markup=back_to_main_keyboard(), parse_mode=ParseMode.MARKDOWN)


@router.message(Command("mj"))
async def cmd_mj(message: Message):
    """Midjourney command."""
    await message.answer(
        "🎨 <b>Midjourney</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 20,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("dalle"))
async def cmd_dalle(message: Message, state: FSMContext):
    """DALLE 3 command."""
    from app.bot.states import MediaState
    from app.bot.handlers.media_handler import cleanup_temp_images

    # Clean up any old images from previous sessions
    await cleanup_temp_images(state)

    text = (
        "🎨 Генерация изображений через DALL·E 3\n\n"
        "Отправьте текстовый промпт, и я сгенерирую изображение."
    )

    await state.set_state(MediaState.waiting_for_image_prompt)
    await state.update_data(service="dalle", reference_image_path=None, photo_caption_prompt=None)

    await message.answer(text, reply_markup=back_to_main_keyboard())


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
    """Photo instruments command - redirect to photo tools menu."""
    from app.bot.keyboards.inline import photo_tools_keyboard

    text = """✂️ **Инструменты для работы с фото**

ℹ️ В этот раздел мы добавили инструменты, которые помогут вам эффективно работать с вашими фотографиями. Выберите интересующий вас инструмент по кнопке ниже.

🔎 **Улучшить качество** — 2,000 токенов
🪄 **Заменить фон** — 15,000 токенов
🪞 **Удалить фон** — 5,000 токенов
📐 **Векторизация** — 5,000 токенов"""

    await message.answer(
        text,
        reply_markup=photo_tools_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(Command("whisper"))
async def cmd_whisper(message: Message, state: FSMContext):
    """Whisper command - voice transcription."""
    from app.bot.states import MediaState

    text = (
        "🎙 **Whisper - Расшифровка голоса**\n\n"
        "OpenAI Whisper распознает речь и превращает её в текст.\n\n"
        "📊 **Возможности:**\n"
        "• Точная расшифровка на русском и других языках\n"
        "• Поддержка различных аудио форматов\n"
        "• Высокая точность распознавания\n\n"
        "💰 **Стоимость:** 1,200 токенов за минуту аудио\n\n"
        "🎵 **Отправьте аудио или голосовое сообщение**"
    )

    await state.set_state(MediaState.waiting_for_whisper_audio)

    await message.answer(text, reply_markup=back_to_main_keyboard(), parse_mode=ParseMode.MARKDOWN)


@router.message(Command("mvideo"))
async def cmd_mvideo(message: Message):
    """Midjourney Video command."""
    await message.answer(
        "🎬 <b>Midjourney Video</b>\n\n⚠️ Функционал в разработке\n\nСтоимость: 30,000 токенов за запрос",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


@router.message(Command("luma"))
async def cmd_luma(message: Message, state):
    """Luma Dream Machine command - directly open Luma interface."""
    from app.bot.keyboards.inline import back_to_main_keyboard
    from app.bot.handlers.media_handler import MediaState

    text = (
        "🌙 **Luma Dream Machine**\n\n"
        "Luma создаёт качественные видео по вашему описанию.\n\n"
        "💰 **Стоимость:** ~8,000 токенов за видео\n\n"
        "🎨 **Режимы работы:**\n"
        "• **Text-to-Video:** Просто отправьте описание видео\n"
        "• **Image-to-Video:** Отправьте фото, затем описание\n\n"
        "✏️ **Отправьте описание видео ИЛИ фото**"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    # Clear old data when starting fresh session
    await state.update_data(service="luma", image_path=None, photo_caption_prompt=None)

    await message.answer(text, reply_markup=back_to_main_keyboard())


@router.message(Command("kling"))
async def cmd_kling(message: Message, state):
    """Kling command - currently under development."""
    from app.bot.keyboards.inline import back_to_main_keyboard

    await state.clear()  # Clear any previous state

    text = (
        "🎞 **Kling AI**\n\n"
        "⚠️ **Функционал в разработке**\n\n"
        "Интеграция с Kling находится в процессе разработки.\n"
        "Пожалуйста, используйте альтернативные сервисы:\n\n"
        "**Для видео:**\n"
        "• 🌊 Veo 3.1\n"
        "• 🎥 Hailuo\n"
        "• 📹 Luma Dream Machine\n\n"
        "**Для изображений:**\n"
        "• 🍌 Nano Banana (Gemini 2.5 Flash)\n"
        "• 🍌✨ Banana PRO (Gemini 3 Pro)\n"
        "• 🖼 DALL·E 3\n\n"
        "Следите за обновлениями!"
    )

    await message.answer(text, reply_markup=back_to_main_keyboard())


@router.message(Command("hailuo"))
async def cmd_hailuo(message: Message, state):
    """Hailuo command - directly open Hailuo interface."""
    from app.bot.keyboards.inline import back_to_main_keyboard
    from app.bot.handlers.media_handler import MediaState, cleanup_temp_images

    # Clean up any old images from previous sessions
    await cleanup_temp_images(state)

    text = (
        "**Hailuo (MiniMax)**\n\n"
        "Hailuo создаёт реалистичные видео.\n\n"
        "💰 **Стоимость:** ~7,000 токенов за видео\n\n"
        "✏️ **Отправьте текстовое описание видео**"
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    # Clear old data when starting fresh session
    await state.update_data(service="hailuo", image_path=None, photo_caption_prompt=None)

    await message.answer(text, reply_markup=back_to_main_keyboard())


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
        "🤝�� **Партнерство**\n\n⚠️ Функционал в разработке",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()
