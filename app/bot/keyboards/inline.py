"""
Inline keyboards for the bot.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


MENU_BUTTONS = [
    ("Главное меню", "bot.back"),
    ("Мой профиль", "bot.profile"),
    ("Оформить подписку", "bot#shop"),
    ("Пригласи друга", "bot.refferal_program"),
    ("Выбрать модель", "bot.llm_models"),
    ("Nano Banana", "bot.nano"),
    ("Nano Banana 2", "bot.nano_banana_2"),
    ("Midjourney", "bot.midjourney"),
    ("Veo 3.1", "bot.veo"),
    ("Kling", "bot.kling_main"),
    ("Kling 3", "bot.kling3"),
    ("Kling O1", "bot.kling_o1"),
    ("Hailuo", "bot.hailuo"),
    ("Midjourney Video", "bot.mjvideo"),
    ("Luma", "bot.luma"),
    ("Suno", "bot.suno"),
    ("Расшифровка голоса", "bot.whisper"),
    ("Работа с фото", "bot.pi"),
    ("Recraft", "bot.recraft"),
    ("Замена лица на фото", "bot.faceswap"),
    ("Активировать промокод", "activate_promocode"),
    ("Помощь", "help"),
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Full menu keyboard."""
    builder = InlineKeyboardBuilder()

    for text, callback in MENU_BUTTONS:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback))

    return builder.as_markup()


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Меню", callback_data="bot.menu"))
    return builder.as_markup()


def ai_models_keyboard() -> InlineKeyboardMarkup:
    """AI models selection keyboard with groups: ChatGPT, Deepseek, Gemini, Others."""
    builder = InlineKeyboardBuilder()

    # ChatGPT — GPT-5.5 first (most powerful)
    builder.row(
        InlineKeyboardButton(text="🚀 GPT 5.5 — самая мощная", callback_data="bot.start_chatgpt_dialog_340")
    )
    builder.row(
        InlineKeyboardButton(text="4️⃣ GPT 4.1 Mini", callback_data="bot.start_chatgpt_dialog_324"),
        InlineKeyboardButton(text="4️⃣ GPT 4o", callback_data="bot.start_chatgpt_dialog_325")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 GPT 5 Mini", callback_data="bot.start_chatgpt_dialog_337"),
        InlineKeyboardButton(text="💫 O3 Mini", callback_data="bot.start_chatgpt_dialog_326")
    )

    # Deepseek
    builder.row(
        InlineKeyboardButton(text="🐳 Deepseek Чат", callback_data="bot.start_chatgpt_dialog_327"),
        InlineKeyboardButton(text="🐳 Deepseek R1", callback_data="bot.start_chatgpt_dialog_328")
    )

    # Gemini
    builder.row(
        InlineKeyboardButton(text="⚡ Gemini Flash 2.0", callback_data="bot.start_chatgpt_dialog_329")
    )

    # Другие модели
    builder.row(
        InlineKeyboardButton(text="📔 Claude 4", callback_data="bot.start_chatgpt_dialog_333"),
        InlineKeyboardButton(text="🌐 Sonar с поиском", callback_data="bot.start_chatgpt_dialog_331")
    )
    builder.row(
        InlineKeyboardButton(text="💻 Sonar Pro", callback_data="bot.start_chatgpt_dialog_332")
    )

    # Инструменты
    builder.row(
        InlineKeyboardButton(text="💬 Выбрать диалог", callback_data="bot.dialogs_chatgpt")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def dialog_keyboard(dialog_id: int, history_enabled: bool = False, show_costs: bool = False, from_home: bool = False) -> InlineKeyboardMarkup:
    """Dialog keyboard with history and cost toggles."""
    builder = InlineKeyboardBuilder()

    # History toggle
    if history_enabled:
        builder.row(
            InlineKeyboardButton(
                text="🟢 История включена",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#sh_1"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔴 История отключена",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#sh_0"
            )
        )

    # Show costs toggle
    if show_costs:
        builder.row(
            InlineKeyboardButton(
                text="🟢 Показ затрат включен",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#bi_1"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔴 Показ затрат отключен",
                callback_data=f"bot.start_chatgpt_dialog_{dialog_id}#bi_0"
            )
        )

    # Change model
    builder.row(
        InlineKeyboardButton(text="🤖 Изменить модель", callback_data="bot.llm_models")
    )

    # Back button
    if from_home:
        builder.row(
            InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад к моделям", callback_data="bot.llm_models")
        )

    return builder.as_markup()


def nano_banana_keyboard(is_pro: bool = False) -> InlineKeyboardMarkup:
    """Nano Banana keyboard with version toggle."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📐 Изменить формат", callback_data="bot.nb.prms:ratio")
    )

    # New button for multiple images generation
    builder.row(
        InlineKeyboardButton(text="🎨 Создать несколько изображений", callback_data="bot.nb.multi")
    )

    # Version toggle button
    if is_pro:
        builder.row(
            InlineKeyboardButton(text="🍌 Переключить на обычную версию", callback_data="bot.nano")
        )
    else:
        builder.row(
            InlineKeyboardButton(text="✨ Переключить на PRO версию", callback_data="bot.nano_pro")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def nano_banana_photo_upsell_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown when user sends a photo to regular Nano Banana."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✨ Сгенерировать в PRO (25 000 токенов)", callback_data="bot.nano_pro")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="bot.back")
    )
    return builder.as_markup()


def nano_format_keyboard(current_ratio: str = "auto") -> InlineKeyboardMarkup:
    """Nano Banana format selection keyboard with current selection marked."""
    builder = InlineKeyboardBuilder()

    # Define all available ratios
    ratios = ["1:1", "2:3", "3:2", "16:9", "9:16", "auto"]

    # Add checkmark to selected ratio
    def format_button_text(ratio: str) -> str:
        return f"✅ {ratio}" if ratio == current_ratio else ratio

    builder.row(
        InlineKeyboardButton(text=format_button_text("1:1"), callback_data="bot.nb.prms.chs:ratio|1:1"),
        InlineKeyboardButton(text=format_button_text("2:3"), callback_data="bot.nb.prms.chs:ratio|2:3"),
        InlineKeyboardButton(text=format_button_text("3:2"), callback_data="bot.nb.prms.chs:ratio|3:2")
    )
    builder.row(
        InlineKeyboardButton(text=format_button_text("16:9"), callback_data="bot.nb.prms.chs:ratio|16:9"),
        InlineKeyboardButton(text=format_button_text("9:16"), callback_data="bot.nb.prms.chs:ratio|9:16"),
        InlineKeyboardButton(text=format_button_text("auto"), callback_data="bot.nb.prms.chs:ratio|auto")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться в Nano Banana", callback_data="bot.nano")
    )

    return builder.as_markup()


def nano_multi_images_keyboard() -> InlineKeyboardMarkup:
    """Nano Banana multiple images count selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="2️⃣ изображения", callback_data="bot.nb.multi.cnt:2"),
        InlineKeyboardButton(text="3️⃣ изображения", callback_data="bot.nb.multi.cnt:3")
    )
    builder.row(
        InlineKeyboardButton(text="4️⃣ изображения", callback_data="bot.nb.multi.cnt:4"),
        InlineKeyboardButton(text="5️⃣ изображений", callback_data="bot.nb.multi.cnt:5")
    )
    builder.row(
        InlineKeyboardButton(text="6️⃣ изображений", callback_data="bot.nb.multi.cnt:6"),
        InlineKeyboardButton(text="🔟 изображений", callback_data="bot.nb.multi.cnt:10")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться в Nano Banana", callback_data="bot.nano")
    )

    return builder.as_markup()


def dialogs_keyboard() -> InlineKeyboardMarkup:
    """Dialogs list keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔍 Анализ текста", callback_data="bot.start_chatgpt_dialog_335"),
        InlineKeyboardButton(text="🌆 Генератор промптов", callback_data="bot.start_chatgpt_dialog_336")
    )
    builder.row(
        InlineKeyboardButton(text="🤖 Выбрать модель", callback_data="bot.llm_models"),
        InlineKeyboardButton(text="🆕 Создать диалог", callback_data="bot.create_chatgpt_dialog")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def create_photo_keyboard() -> InlineKeyboardMarkup:
    """Photo creation keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🖼 GPT Image 2", callback_data="bot.gpt_image_2")
    )
    builder.row(
        InlineKeyboardButton(text="🍌 Nano Banana", callback_data="bot.nano"),
        InlineKeyboardButton(text="🍌✨ Banana PRO", callback_data="bot.nano_pro")
    )
    builder.row(
        InlineKeyboardButton(text="🍌 Nano Banana 2", callback_data="bot.nano_banana_2")
    )
    builder.row(
        InlineKeyboardButton(text="✨ Seedream 4.5", callback_data="bot.seedream_4.5"),
        InlineKeyboardButton(text="✨ Seedream 5.0", callback_data="bot.seedream_5.0")
    )
    builder.row(
        InlineKeyboardButton(text="🌆 Midjourney", callback_data="bot.midjourney")
    )
    builder.row(
        InlineKeyboardButton(text="👁 GPT Vision", callback_data="bot.gpt_vision")
    )
    builder.row(
        InlineKeyboardButton(text="🛠 Редактировать фото", callback_data="bot.pi")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def create_video_keyboard() -> InlineKeyboardMarkup:
    """Video creation keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🌊 Veo 3.1", callback_data="bot.veo"),
        InlineKeyboardButton(text="🎥 Hailuo", callback_data="bot.hailuo")
    )
    builder.row(
        InlineKeyboardButton(text="🎞 Kling", callback_data="bot.kling_main"),
        InlineKeyboardButton(text="📹 Luma", callback_data="bot.luma")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Kling 3", callback_data="bot.kling3"),
        InlineKeyboardButton(text="🧠 Kling O1", callback_data="bot.kling_o1"),
    )
    builder.row(
        InlineKeyboardButton(text="🌆 Midjourney", callback_data="bot.mjvideo"),
        InlineKeyboardButton(text="✨ Kling Эффекты", callback_data="bot.kling_effects")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def gpt_image_2_keyboard(size: str = "auto", quality: str = "auto") -> InlineKeyboardMarkup:
    """GPT Image 2 settings keyboard."""
    builder = InlineKeyboardBuilder()

    size_labels = {
        "auto": "Авто",
        "1024x1024": "1:1 (1024×1024)",
        "1536x1024": "3:2 горизонт. (1536×1024)",
        "1024x1536": "2:3 вертикаль (1024×1536)",
        "2048x2048": "2K 1:1 (2048×2048)",
        "2048x1152": "2K 16:9 (2048×1152)",
        "3840x2160": "4K горизонт. (3840×2160)",
        "2160x3840": "4K вертикаль (2160×3840)",
    }
    quality_labels = {
        "auto": "Авто",
        "low": "Низкое ⚡",
        "medium": "Среднее ⭐",
        "high": "Высокое 💎",
    }

    builder.row(
        InlineKeyboardButton(
            text=f"📐 Формат: {size_labels.get(size, size)}",
            callback_data="bot.gi2:size_menu"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"✨ Качество: {quality_labels.get(quality, quality)}",
            callback_data="bot.gi2:quality_menu"
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def gpt_image_2_size_keyboard() -> InlineKeyboardMarkup:
    """GPT Image 2 size selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Авто (рекомендуется)", callback_data="bot.gi2:size:auto"))
    builder.row(InlineKeyboardButton(text="◾ 1:1  1024×1024", callback_data="bot.gi2:size:1024x1024"))
    builder.row(InlineKeyboardButton(text="▬ 3:2  1536×1024 (горизонталь)", callback_data="bot.gi2:size:1536x1024"))
    builder.row(InlineKeyboardButton(text="▮ 2:3  1024×1536 (вертикаль)", callback_data="bot.gi2:size:1024x1536"))
    builder.row(InlineKeyboardButton(text="⬛ 2K  2048×2048", callback_data="bot.gi2:size:2048x2048"))
    builder.row(InlineKeyboardButton(text="📺 2K 16:9  2048×1152", callback_data="bot.gi2:size:2048x1152"))
    builder.row(InlineKeyboardButton(text="🖥 4K  3840×2160 (горизонталь)", callback_data="bot.gi2:size:3840x2160"))
    builder.row(InlineKeyboardButton(text="📱 4K  2160×3840 (вертикаль)", callback_data="bot.gi2:size:2160x3840"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="bot.gpt_image_2"))
    return builder.as_markup()


def gpt_image_2_quality_keyboard() -> InlineKeyboardMarkup:
    """GPT Image 2 quality selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⚡ Низкое (быстро, дешевле)", callback_data="bot.gi2:quality:low"))
    builder.row(InlineKeyboardButton(text="⭐ Среднее (баланс)", callback_data="bot.gi2:quality:medium"))
    builder.row(InlineKeyboardButton(text="💎 Высокое (лучшее качество)", callback_data="bot.gi2:quality:high"))
    builder.row(InlineKeyboardButton(text="🔄 Авто", callback_data="bot.gi2:quality:auto"))
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="bot.gpt_image_2"))
    return builder.as_markup()


def photo_tools_keyboard() -> InlineKeyboardMarkup:
    """Photo tools keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔎 Улучшить качество", callback_data="bot.pi_upscale")
    )
    builder.row(
        InlineKeyboardButton(text="🪄 Заменить фон", callback_data="bot.pi_repb")
    )
    builder.row(
        InlineKeyboardButton(text="🪞 Удалить фон", callback_data="bot.pi_remb")
    )
    builder.row(
        InlineKeyboardButton(text="📐 Векторизация", callback_data="bot.pi_vect")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def audio_tools_keyboard() -> InlineKeyboardMarkup:
    """Audio tools keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎧 Создать песню", callback_data="bot.suno")
    )
    builder.row(
        InlineKeyboardButton(text="🎙 Расшифровка голоса", callback_data="bot.whisper")
    )
    builder.row(
        InlineKeyboardButton(text="🗣 Озвучка текста", callback_data="bot.whisper_tts")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def subscription_keyboard() -> InlineKeyboardMarkup:
    """Subscription selection keyboard with new billing prices."""
    from app.core.subscription_plans import list_subscription_plans

    builder = InlineKeyboardBuilder()

    for plan in list_subscription_plans():
        builder.row(
            InlineKeyboardButton(
                text=(
                    f"{plan.display_name} — {plan.price} руб."
                ),
                callback_data=f"shop_select_tariff_{plan.plan_id}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="🔥 2 500 000 токенов — 1459 руб.",
            callback_data="shop_select_tariff_22"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔹 Купить вечные токены",
            callback_data="bot#shop_tokens"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔢 Активировать промокод",
            callback_data="activate_promocode"
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.back")
    )

    return builder.as_markup()


def eternal_tokens_keyboard() -> InlineKeyboardMarkup:
    """Eternal tokens selection keyboard."""
    from app.core.subscription_plans import ETERNAL_PLANS
    from app.core.billing_config import format_token_amount

    builder = InlineKeyboardBuilder()

    for plan in ETERNAL_PLANS.values():
        builder.row(
            InlineKeyboardButton(
                text=f"{format_token_amount(plan.tokens)} токенов — {plan.price} руб.",
                callback_data=f"buy:{plan.subscription_type}"
            )
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot#shop")
    )

    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    """Profile keyboard with additional options."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💎 Токены", callback_data="bot.profile_tokens")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои платежи", callback_data="bot.profile_payments"),
        InlineKeyboardButton(text="📦 Мои подписки", callback_data="bot.profile_subscriptions")
    )
    builder.row(
        InlineKeyboardButton(text="🤝 Партнерство", callback_data="bot.refferal_program")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Поддержка", callback_data="page#faq")
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Активировать промокод", callback_data="activate_promocode")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def referral_keyboard(user_telegram_id: int = None) -> InlineKeyboardMarkup:
    """Referral program keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🏦 Вывести средства", callback_data="bot.refferal_withdraw")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Обменять на токены", callback_data="bot.refferal_exchange")
    )

    # Share button with dynamic referral link
    if user_telegram_id:
        bot_username = "assistantvirtualsbot"
        referral_link = f"https://t.me/{bot_username}?start=ref{user_telegram_id}"
        share_url = f"https://t.me/share/url?url={referral_link}"
        builder.row(
            InlineKeyboardButton(
                text="🔗 Поделиться ссылкой",
                url=share_url
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.profile")
    )

    return builder.as_markup()


def help_keyboard() -> InlineKeyboardMarkup:
    """Help menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💎 Токены", callback_data="help.tokens")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Платежи", callback_data="help.payments")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.profile")
    )

    return builder.as_markup()


def subscription_manage_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    """Keyboard for managing an active subscription."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="❌ Отменить подписку", callback_data=f"cancel_subscription_{subscription_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="bot.profile")
    )

    return builder.as_markup()


def kling_choice_keyboard() -> InlineKeyboardMarkup:
    """Kling AI choice keyboard for video or motion control generation."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎬 Создать видео", callback_data="bot.kling_video")
    )
    builder.row(
        InlineKeyboardButton(text="🕺 Motion Control", callback_data="bot.kling_motion_control")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


# ======================
# KLING VIDEO KEYBOARDS
# ======================

def kling_main_keyboard() -> InlineKeyboardMarkup:
    """Main Kling video keyboard with settings button."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="kling.settings")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def kling_settings_keyboard() -> InlineKeyboardMarkup:
    """Kling settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📐 Формат видео", callback_data="kling.settings.aspect_ratio")
    )
    builder.row(
        InlineKeyboardButton(text="🕓 Длительность", callback_data="kling.settings.duration")
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Версия", callback_data="kling.settings.version")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Автоперевод", callback_data="kling.settings.auto_translate")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_aspect_ratio_keyboard(current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """Kling aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "16:9", "9:16"]

    for ratio in ratios:
        text = f"✅ {ratio}" if ratio == current_ratio else ratio
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling.set.aspect_ratio:{ratio}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_duration_keyboard(current_duration: int = 5) -> InlineKeyboardMarkup:
    """Kling duration selection keyboard."""
    builder = InlineKeyboardBuilder()

    durations = [5, 10]

    for duration in durations:
        text = f"✅ {duration} секунд" if duration == current_duration else f"{duration} секунд"
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling.set.duration:{duration}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_version_keyboard(current_version: str = "2.5") -> InlineKeyboardMarkup:
    """Kling version selection keyboard."""
    builder = InlineKeyboardBuilder()

    versions = ["2.1", "2.1 Pro", "2.5", "2.6"]

    for version in versions:
        text = f"✅ {version}" if version == current_version else version
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling.set.version:{version}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


def kling_auto_translate_keyboard(current_value: bool = True) -> InlineKeyboardMarkup:
    """Kling auto-translate toggle keyboard."""
    builder = InlineKeyboardBuilder()

    yes_text = "✅ Да" if current_value else "Да"
    no_text = "✅ Нет" if not current_value else "Нет"

    builder.row(
        InlineKeyboardButton(text=yes_text, callback_data="kling.set.auto_translate:yes")
    )
    builder.row(
        InlineKeyboardButton(text=no_text, callback_data="kling.set.auto_translate:no")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_video")
    )

    return builder.as_markup()


# ======================
# KLING IMAGE KEYBOARDS
# ======================

def kling_image_main_keyboard() -> InlineKeyboardMarkup:
    """Main Kling image keyboard with settings button."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="kling_image.settings")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def kling_image_settings_keyboard() -> InlineKeyboardMarkup:
    """Kling image settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📐 Формат изображения", callback_data="kling_image.settings.aspect_ratio")
    )
    builder.row(
        InlineKeyboardButton(text="🔢 Версия модели", callback_data="kling_image.settings.model")
    )
    builder.row(
        InlineKeyboardButton(text="📏 Разрешение", callback_data="kling_image.settings.resolution")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Автоперевод", callback_data="kling_image.settings.auto_translate")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_main")
    )

    return builder.as_markup()


def kling_image_aspect_ratio_keyboard(current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """Kling image aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]

    for ratio in ratios:
        text = f"✅ {ratio}" if ratio == current_ratio else ratio
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling_image.set.aspect_ratio:{ratio}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_image.settings")
    )

    return builder.as_markup()


def kling_image_model_keyboard(current_model: str = "kling-v1") -> InlineKeyboardMarkup:
    """Kling image model selection keyboard."""
    builder = InlineKeyboardBuilder()

    models = [
        ("kling-v1", "Kling v1"),
        ("kling-v1-5", "Kling v1.5 (face/subject reference)"),
        ("kling-v2", "Kling v2"),
    ]

    for model_id, model_name in models:
        text = f"✅ {model_name}" if model_id == current_model else model_name
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling_image.set.model:{model_id}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_image.settings")
    )

    return builder.as_markup()


def kling_image_resolution_keyboard(current_resolution: str = "1k") -> InlineKeyboardMarkup:
    """Kling image resolution selection keyboard."""
    builder = InlineKeyboardBuilder()

    resolutions = [
        ("1k", "1K (стандартное)"),
        ("2k", "2K (высокое)"),
    ]

    for res_id, res_name in resolutions:
        text = f"✅ {res_name}" if res_id == current_resolution else res_name
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling_image.set.resolution:{res_id}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_image.settings")
    )

    return builder.as_markup()


def kling_image_auto_translate_keyboard(current_value: bool = True) -> InlineKeyboardMarkup:
    """Kling image auto-translate toggle keyboard."""
    builder = InlineKeyboardBuilder()

    yes_text = "✅ Да" if current_value else "Да"
    no_text = "✅ Нет" if not current_value else "Нет"

    builder.row(
        InlineKeyboardButton(text=yes_text, callback_data="kling_image.set.auto_translate:yes")
    )
    builder.row(
        InlineKeyboardButton(text=no_text, callback_data="kling_image.set.auto_translate:no")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_image.settings")
    )

    return builder.as_markup()


# ======================
# KLING EFFECTS KEYBOARDS
# ======================

def kling_effects_main_keyboard() -> InlineKeyboardMarkup:
    """Main Kling effects keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎭 Выбрать эффект", callback_data="kling_effects.categories")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def kling_effects_categories_keyboard() -> InlineKeyboardMarkup:
    """Kling effects categories selection keyboard."""
    from app.services.video.kling_effects_service import EFFECT_CATEGORIES

    builder = InlineKeyboardBuilder()

    # Add category buttons in rows of 2
    categories = list(EFFECT_CATEGORIES.items())
    for i in range(0, len(categories), 2):
        row_items = categories[i:i+2]
        buttons = [
            InlineKeyboardButton(
                text=cat_data["name"],
                callback_data=f"kling_effects.category:{cat_id}"
            )
            for cat_id, cat_data in row_items
        ]
        builder.row(*buttons)

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.kling_effects")
    )

    return builder.as_markup()


def kling_effects_list_keyboard(category: str, page: int = 0, per_page: int = 8) -> InlineKeyboardMarkup:
    """Kling effects list for a category with pagination."""
    from app.services.video.kling_effects_service import get_effects_by_category

    builder = InlineKeyboardBuilder()
    effects = get_effects_by_category(category)

    # Paginate effects
    start = page * per_page
    end = start + per_page
    page_effects = effects[start:end]

    # Add effect buttons
    for effect in page_effects:
        effect_id = effect[0]
        effect_name = effect[1]
        is_dual = len(effect) > 2 and effect[2] is True

        builder.row(
            InlineKeyboardButton(
                text=effect_name,
                callback_data=f"kling_effects.select:{effect_id}"
            )
        )

    # Pagination buttons
    total_pages = (len(effects) + per_page - 1) // per_page
    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"kling_effects.page:{category}:{page-1}"
                )
            )
        if page < total_pages - 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="Вперёд ▶️",
                    callback_data=f"kling_effects.page:{category}:{page+1}"
                )
            )
        if nav_buttons:
            builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="📁 Категории", callback_data="kling_effects.categories")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def kling_effects_confirm_keyboard(effect_id: str) -> InlineKeyboardMarkup:
    """Confirm effect selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"kling_effects.confirm:{effect_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Выбрать другой эффект", callback_data="kling_effects.categories")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


# ======================
# KLING MOTION CONTROL KEYBOARDS
# ======================

def kling_motion_control_keyboard(mode: str = "std", orientation: str = "image", keep_sound: str = "yes") -> InlineKeyboardMarkup:
    """Main Kling Motion Control keyboard with settings."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="kling_mc.settings")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling", callback_data="bot.kling_main")
    )

    return builder.as_markup()


def kling_mc_settings_keyboard() -> InlineKeyboardMarkup:
    """Kling Motion Control settings keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎯 Режим (std/pro)", callback_data="kling_mc.settings.mode")
    )
    builder.row(
        InlineKeyboardButton(text="🧍 Ориентация персонажа", callback_data="kling_mc.settings.orientation")
    )
    builder.row(
        InlineKeyboardButton(text="🔊 Звук из видео", callback_data="kling_mc.settings.sound")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.kling_motion_control")
    )

    return builder.as_markup()


def kling_mc_mode_keyboard(current_mode: str = "std") -> InlineKeyboardMarkup:
    """Kling Motion Control mode selection keyboard."""
    builder = InlineKeyboardBuilder()

    modes = [
        ("std", "Стандартный (быстрый)"),
        ("pro", "Профессиональный (качественный)"),
    ]

    for mode_value, mode_name in modes:
        prefix = "✅ " if current_mode == mode_value else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{mode_name}",
                callback_data=f"kling_mc.set.mode:{mode_value}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_mc.settings")
    )

    return builder.as_markup()


def kling_mc_orientation_keyboard(current: str = "image") -> InlineKeyboardMarkup:
    """Kling Motion Control character orientation keyboard."""
    builder = InlineKeyboardBuilder()

    options = [
        ("image", "По изображению (макс. 10 сек.)"),
        ("video", "По видео (макс. 30 сек.)"),
    ]

    for val, name in options:
        prefix = "✅ " if current == val else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{name}",
                callback_data=f"kling_mc.set.orientation:{val}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_mc.settings")
    )

    return builder.as_markup()


def kling_mc_sound_keyboard(current: str = "yes") -> InlineKeyboardMarkup:
    """Kling Motion Control sound settings keyboard."""
    builder = InlineKeyboardBuilder()

    options = [
        ("yes", "Сохранить звук"),
        ("no", "Без звука"),
    ]

    for val, name in options:
        prefix = "✅ " if current == val else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{name}",
                callback_data=f"kling_mc.set.sound:{val}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="kling_mc.settings")
    )

    return builder.as_markup()


# ======================
# KLING 3.0 KEYBOARDS
# ======================

def kling3_main_keyboard() -> InlineKeyboardMarkup:
    """Main Kling 3.0 video keyboard with settings and instruction buttons."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="kling3.settings")
    )
    builder.row(
        InlineKeyboardButton(text="📖 Инструкция", callback_data="kling3.instruction")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def kling3_settings_keyboard() -> InlineKeyboardMarkup:
    """Kling 3.0 settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📺 Разрешение", callback_data="kling3.settings.mode")
    )
    builder.row(
        InlineKeyboardButton(text="📐 Формат видео", callback_data="kling3.settings.aspect_ratio")
    )
    builder.row(
        InlineKeyboardButton(text="🕓 Длительность", callback_data="kling3.settings.duration")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Автоперевод", callback_data="kling3.settings.auto_translate")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling 3", callback_data="bot.kling3")
    )

    return builder.as_markup()


def kling3_mode_keyboard(current_mode: str = "std") -> InlineKeyboardMarkup:
    """Kling 3.0 resolution mode selection keyboard (std=720p, pro=1080p)."""
    builder = InlineKeyboardBuilder()

    modes = [
        ("std", "720p"),
        ("pro", "1080p"),
    ]

    for mode_val, mode_name in modes:
        text = f"✅ {mode_name}" if mode_val == current_mode else mode_name
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling3.set.mode:{mode_val}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling 3", callback_data="bot.kling3")
    )

    return builder.as_markup()


def kling3_aspect_ratio_keyboard(current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """Kling 3.0 aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "16:9", "9:16"]

    for ratio in ratios:
        text = f"✅ {ratio}" if ratio == current_ratio else ratio
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling3.set.aspect_ratio:{ratio}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling 3", callback_data="bot.kling3")
    )

    return builder.as_markup()


def kling3_duration_keyboard(current_duration: int = 5) -> InlineKeyboardMarkup:
    """Kling 3.0 duration selection keyboard (5, 10, 15 seconds)."""
    builder = InlineKeyboardBuilder()

    durations = [5, 10, 15]

    for duration in durations:
        text = f"✅ {duration} сек" if duration == current_duration else f"{duration} сек"
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling3.set.duration:{duration}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling 3", callback_data="bot.kling3")
    )

    return builder.as_markup()


def kling3_auto_translate_keyboard(current_value: bool = True) -> InlineKeyboardMarkup:
    """Kling 3.0 auto-translate toggle keyboard."""
    builder = InlineKeyboardBuilder()

    yes_text = "✅ Да" if current_value else "Да"
    no_text = "✅ Нет" if not current_value else "Нет"

    builder.row(
        InlineKeyboardButton(text=yes_text, callback_data="kling3.set.auto_translate:yes")
    )
    builder.row(
        InlineKeyboardButton(text=no_text, callback_data="kling3.set.auto_translate:no")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling 3", callback_data="bot.kling3")
    )

    return builder.as_markup()


# ======================
# SUNO KEYBOARDS
# ======================

def suno_main_keyboard(model_version: str = "V5", is_instrumental: bool = False, style: str = "техно, хип-хоп", balance_songs: int = 0, tokens_per_song: int = 17600) -> InlineKeyboardMarkup:
    """Main Suno keyboard with current settings."""
    builder = InlineKeyboardBuilder()

    # Type button
    type_text = "инструментал (без слов)" if is_instrumental else "с текстом песни"

    builder.row(
        InlineKeyboardButton(text="⚙️ Параметры", callback_data="suno.settings")
    )
    builder.row(
        InlineKeyboardButton(text="📝 Создать песню пошагово", callback_data="suno.step_by_step")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def suno_settings_keyboard(model_version: str = "V5", is_instrumental: bool = False, style: str = "техно, хип-хоп") -> InlineKeyboardMarkup:
    """Suno settings keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📀 Изменить версию", callback_data="suno.change_version")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Изменить тип", callback_data="suno.change_type")
    )
    builder.row(
        InlineKeyboardButton(text="🎨 Изменить стиль", callback_data="suno.change_style")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_version_keyboard() -> InlineKeyboardMarkup:
    """Suno model version selection keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎵 V5 (лучшее)", callback_data="suno.set_version_V5")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 V4.5 Plus", callback_data="suno.set_version_V4_5PLUS"),
        InlineKeyboardButton(text="🎵 V4.5 All", callback_data="suno.set_version_V4_5ALL")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 V4.5", callback_data="suno.set_version_V4_5"),
        InlineKeyboardButton(text="🎵 V4", callback_data="suno.set_version_V4")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="suno.settings")
    )

    return builder.as_markup()


def suno_type_keyboard() -> InlineKeyboardMarkup:
    """Suno type selection keyboard (instrumental or with lyrics)."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎤 С текстом песни", callback_data="suno.set_type_lyrics")
    )
    builder.row(
        InlineKeyboardButton(text="🎹 Инструментал (без слов)", callback_data="suno.set_type_instrumental")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="suno.settings")
    )

    return builder.as_markup()


def suno_style_keyboard(selected_styles: list = None) -> InlineKeyboardMarkup:
    """Suno style selection keyboard with multiple selection support."""
    builder = InlineKeyboardBuilder()

    if selected_styles is None:
        selected_styles = []

    # All 21 styles from the image (7 rows x 3 columns)
    styles = [
        ("🎤 Рэп", "рэп"),
        ("🎧 Хип-хоп", "хип-хоп"),
        ("🎸 Рок", "рок"),

        ("🎹 Поп", "поп"),
        ("🎵 R&B", "r&b"),
        ("⚡ Электроника", "электроника"),

        ("🪩 Диско", "диско"),
        ("🔊 Техно", "техно"),
        ("🏠 Хаус", "хаус"),

        ("💃 Танцевальная", "танцевальная"),
        ("🎛 Дабстеп", "дабстеп"),
        ("🎺 Джаз", "джаз"),

        ("🤠 Кантри", "кантри"),
        ("🌴 Регги", "регги"),
        ("🎻 Фолк", "фолк"),

        ("🎷 Блюз", "блюз"),
        ("🎼 Классика", "классическая"),
        ("🎸 Фанк", "фанк"),

        ("🎭 Панк", "панк"),
        ("🌊 Эмбиент", "эмбиент"),
        ("📻 Lo-Fi", "lo-fi"),
    ]

    # Build keyboard in rows of 3
    for i in range(0, len(styles), 3):
        row_buttons = []
        for j in range(3):
            if i + j < len(styles):
                style_name, style_value = styles[i + j]
                # Add checkmark if selected
                if style_value in selected_styles:
                    style_name = f"✅ {style_name}"
                row_buttons.append(
                    InlineKeyboardButton(
                        text=style_name,
                        callback_data=f"suno.toggle_style_{style_value}"
                    )
                )
        builder.row(*row_buttons)

    # Show selected styles count and confirm button
    selected_count = len(selected_styles)
    if selected_count > 0:
        builder.row(
            InlineKeyboardButton(
                text=f"👍 Я выбрал(а) стили ({selected_count}/3)",
                callback_data="suno.confirm_styles"
            )
        )

    builder.row(
        InlineKeyboardButton(text="✏️ Ввести свой стиль", callback_data="suno.custom_style")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Вернуться в Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_lyrics_choice_keyboard(song_title: str) -> InlineKeyboardMarkup:
    """Keyboard for choosing how to create lyrics."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🤖 Создать по названию", callback_data="suno.lyrics_by_title")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Создать по описанию", callback_data="suno.lyrics_by_description")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Написать свой текст", callback_data="suno.lyrics_custom")
    )
    builder.row(
        InlineKeyboardButton(text="🎹 Создать без слов", callback_data="suno.lyrics_instrumental")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back to Suno keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )
    return builder.as_markup()


def suno_vocal_keyboard(selected_vocal: str = "m") -> InlineKeyboardMarkup:
    """Keyboard for selecting vocal type."""
    builder = InlineKeyboardBuilder()

    # Vocal type buttons with checkmark for selected
    # API supports: 'm' (male), 'f' (female)
    vocals = [
        ("👨 Мужской голос", "m"),
        ("👩 Женский голос", "f"),
    ]

    for text, vocal_type in vocals:
        if vocal_type == selected_vocal:
            text = f"✅ {text}"
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"suno.set_vocal_{vocal_type}")
        )

    builder.row(
        InlineKeyboardButton(text="👍 Подтвердить", callback_data="suno.confirm_vocal")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )

    return builder.as_markup()


def suno_final_keyboard() -> InlineKeyboardMarkup:
    """Final screen keyboard with generate button."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎵 Создать песню", callback_data="suno.generate_song")
    )
    builder.row(
        InlineKeyboardButton(text="↻ Начать заново", callback_data="suno.step_by_step")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться к Suno", callback_data="bot.suno")
    )
    return builder.as_markup()


# =============================================
# SEEDREAM KEYBOARDS
# =============================================

def seedream_keyboard(
    current_resolution: str = "2K",
    current_aspect_ratio: str = "auto",
    batch_mode: bool = False,
) -> InlineKeyboardMarkup:
    """Seedream 4.5 main keyboard with settings."""
    builder = InlineKeyboardBuilder()

    # Resolution selection
    builder.row(
        InlineKeyboardButton(
            text=f"📐 Разрешение: {current_resolution}",
            callback_data="seedream.settings.resolution"
        )
    )

    # Aspect ratio selection
    builder.row(
        InlineKeyboardButton(
            text=f"🖼 Формат: {current_aspect_ratio}",
            callback_data="seedream.settings.aspect_ratio"
        )
    )

    # Batch mode toggle
    if batch_mode:
        builder.row(
            InlineKeyboardButton(
                text="📦 Пакетная генерация: ВКЛ",
                callback_data="seedream.toggle.batch|off"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="🔢 Количество изображений",
                callback_data="seedream.settings.batch_count"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="📦 Пакетная генерация: ВЫКЛ",
                callback_data="seedream.toggle.batch|on"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def seedream_resolution_keyboard(current_resolution: str = "2K") -> InlineKeyboardMarkup:
    """Seedream 4.5 resolution selection keyboard."""
    builder = InlineKeyboardBuilder()

    resolutions = ["2K", "4K"]

    def format_button_text(res: str) -> str:
        return f"✅ {res}" if res == current_resolution else res

    builder.row(
        *[
            InlineKeyboardButton(
                text=format_button_text(res),
                callback_data=f"seedream.set.resolution|{res}"
            )
            for res in resolutions
        ]
    )

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data="bot.seedream_4.5"
        )
    )

    return builder.as_markup()


def seedream_aspect_ratio_keyboard(current_ratio: str = "auto") -> InlineKeyboardMarkup:
    """Seedream 4.5 aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "4:3", "3:4", "16:9", "9:16", "auto"]

    def format_button_text(ratio: str) -> str:
        return f"✅ {ratio}" if ratio == current_ratio else ratio

    builder.row(
        InlineKeyboardButton(text=format_button_text("1:1"), callback_data="seedream.set.aspect_ratio|1:1"),
        InlineKeyboardButton(text=format_button_text("4:3"), callback_data="seedream.set.aspect_ratio|4:3"),
        InlineKeyboardButton(text=format_button_text("3:4"), callback_data="seedream.set.aspect_ratio|3:4"),
    )
    builder.row(
        InlineKeyboardButton(text=format_button_text("16:9"), callback_data="seedream.set.aspect_ratio|16:9"),
        InlineKeyboardButton(text=format_button_text("9:16"), callback_data="seedream.set.aspect_ratio|9:16"),
        InlineKeyboardButton(text=format_button_text("auto"), callback_data="seedream.set.aspect_ratio|auto"),
    )

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data="bot.seedream_4.5"
        )
    )

    return builder.as_markup()


def seedream_batch_count_keyboard(current_count: int = 3) -> InlineKeyboardMarkup:
    """Seedream batch image count selection keyboard."""
    builder = InlineKeyboardBuilder()

    counts = [2, 3, 4, 5, 6, 8, 10, 15]

    def format_button_text(count: int) -> str:
        text = f"{count} шт."
        return f"✅ {text}" if count == current_count else text

    # Build in rows of 4
    for i in range(0, len(counts), 4):
        row_buttons = []
        for j in range(4):
            if i + j < len(counts):
                count = counts[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=format_button_text(count),
                        callback_data=f"seedream.set.batch_count|{count}"
                    )
                )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data="bot.seedream_4.5"
        )
    )

    return builder.as_markup()


def seedream_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back to Seedream keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад к Seedream",
            callback_data="bot.seedream_4.5"
        )
    )
    return builder.as_markup()


# =============================================
# SEEDREAM 5.0 KEYBOARDS
# =============================================

def seedream5_keyboard(
    current_resolution: str = "2K",
    current_aspect_ratio: str = "1:1",
    current_output_format: str = "jpeg",
    batch_mode: bool = False,
    optimize_prompt: bool = False
) -> InlineKeyboardMarkup:
    """Seedream 5.0 Lite main keyboard with settings."""
    builder = InlineKeyboardBuilder()

    # Resolution selection
    builder.row(
        InlineKeyboardButton(
            text=f"📐 Разрешение: {current_resolution}",
            callback_data="seedream5.settings.resolution"
        )
    )

    # Aspect ratio selection
    builder.row(
        InlineKeyboardButton(
            text=f"🖼 Формат: {current_aspect_ratio}",
            callback_data="seedream5.settings.aspect_ratio"
        )
    )

    # Output format selection
    format_display = "JPEG" if current_output_format == "jpeg" else "PNG"
    builder.row(
        InlineKeyboardButton(
            text=f"📄 Формат файла: {format_display}",
            callback_data="seedream5.settings.output_format"
        )
    )

    # Prompt optimization toggle
    if optimize_prompt:
        builder.row(
            InlineKeyboardButton(
                text="🧠 Оптимизация промпта: ВКЛ",
                callback_data="seedream5.toggle.optimize|off"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🧠 Оптимизация промпта: ВЫКЛ",
                callback_data="seedream5.toggle.optimize|on"
            )
        )

    # Batch mode toggle
    if batch_mode:
        builder.row(
            InlineKeyboardButton(
                text="📦 Пакетная генерация: ВКЛ",
                callback_data="seedream5.toggle.batch|off"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="🔢 Количество изображений",
                callback_data="seedream5.settings.batch_count"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="📦 Пакетная генерация: ВЫКЛ",
                callback_data="seedream5.toggle.batch|on"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="bot.create_photo")
    )

    return builder.as_markup()


def seedream5_resolution_keyboard(current_resolution: str = "2K") -> InlineKeyboardMarkup:
    """Seedream 5.0 resolution selection keyboard."""
    builder = InlineKeyboardBuilder()

    resolutions = ["2K", "3K"]

    for res in resolutions:
        text = f"✅ {res}" if res == current_resolution else res
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"seedream5.set.resolution|{res}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="bot.seedream_5.0"
        )
    )

    return builder.as_markup()


def seedream5_aspect_ratio_keyboard(current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """Seedream 5.0 aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = [
        ("1:1", "1:1"),
        ("16:9", "16:9"),
        ("9:16", "9:16"),
        ("4:3", "4:3"),
        ("3:4", "3:4"),
    ]

    def format_button_text(ratio: str) -> str:
        return f"✅ {ratio}" if ratio == current_ratio else ratio

    # Build in rows of 3
    for i in range(0, len(ratios), 3):
        row_buttons = []
        for j in range(3):
            if i + j < len(ratios):
                ratio_name, ratio_value = ratios[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=format_button_text(ratio_name),
                        callback_data=f"seedream5.set.aspect_ratio|{ratio_value}"
                    )
                )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="bot.seedream_5.0"
        )
    )

    return builder.as_markup()


def seedream5_output_format_keyboard(current_format: str = "jpeg") -> InlineKeyboardMarkup:
    """Seedream 5.0 output format selection keyboard."""
    builder = InlineKeyboardBuilder()

    formats = [
        ("JPEG", "jpeg"),
        ("PNG", "png"),
    ]

    for fmt_name, fmt_value in formats:
        text = f"✅ {fmt_name}" if fmt_value == current_format else fmt_name
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"seedream5.set.output_format|{fmt_value}"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="bot.seedream_5.0"
        )
    )

    return builder.as_markup()


def seedream5_batch_count_keyboard(current_count: int = 3) -> InlineKeyboardMarkup:
    """Seedream 5.0 batch image count selection keyboard."""
    builder = InlineKeyboardBuilder()

    counts = [2, 3, 4, 5, 6, 8, 10, 15]

    def format_button_text(count: int) -> str:
        text = f"{count} шт."
        return f"✅ {text}" if count == current_count else text

    for i in range(0, len(counts), 4):
        row_buttons = []
        for j in range(4):
            if i + j < len(counts):
                count = counts[i + j]
                row_buttons.append(
                    InlineKeyboardButton(
                        text=format_button_text(count),
                        callback_data=f"seedream5.set.batch_count|{count}"
                    )
                )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="bot.seedream_5.0"
        )
    )

    return builder.as_markup()


# ======================
# MIDJOURNEY KEYBOARDS
# ======================

def midjourney_main_keyboard() -> InlineKeyboardMarkup:
    """Main Midjourney keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def midjourney_video_main_keyboard() -> InlineKeyboardMarkup:
    """Midjourney Video main keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


# ======================
# KLING O1 KEYBOARDS
# ======================

def kling_o1_main_keyboard(has_media: bool = False) -> InlineKeyboardMarkup:
    """Main Kling O1 keyboard with optional Continue button when media is uploaded."""
    builder = InlineKeyboardBuilder()

    if has_media:
        builder.row(
            InlineKeyboardButton(text="✅ Продолжить", callback_data="kling_o1.continue")
        )
        builder.row(
            InlineKeyboardButton(text="🗑 Очистить медиа", callback_data="kling_o1.clear_media")
        )

    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="kling_o1.settings")
    )
    builder.row(
        InlineKeyboardButton(text="📖 Инструкция", callback_data="kling_o1.instruction")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Создать видео", callback_data="bot.create_video")
    )

    return builder.as_markup()


def kling_o1_settings_keyboard() -> InlineKeyboardMarkup:
    """Kling O1 settings menu keyboard."""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📺 Разрешение", callback_data="kling_o1.settings.mode")
    )
    builder.row(
        InlineKeyboardButton(text="📐 Формат видео", callback_data="kling_o1.settings.aspect_ratio")
    )
    builder.row(
        InlineKeyboardButton(text="🕓 Длительность", callback_data="kling_o1.settings.duration")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Автоперевод", callback_data="kling_o1.settings.auto_translate")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling O1", callback_data="bot.kling_o1")
    )

    return builder.as_markup()


def kling_o1_mode_keyboard(current_mode: str = "std") -> InlineKeyboardMarkup:
    """Kling O1 resolution mode selection (std=1080p, pro=4K)."""
    builder = InlineKeyboardBuilder()

    modes = [
        ("std", "1080p"),
        ("pro", "4K"),
    ]

    for mode_val, mode_name in modes:
        text = f"✅ {mode_name}" if mode_val == current_mode else mode_name
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling_o1.set.mode:{mode_val}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling O1", callback_data="bot.kling_o1")
    )

    return builder.as_markup()


def kling_o1_aspect_ratio_keyboard(current_ratio: str = "1:1") -> InlineKeyboardMarkup:
    """Kling O1 aspect ratio selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "16:9", "9:16"]

    for ratio in ratios:
        text = f"✅ {ratio}" if ratio == current_ratio else ratio
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling_o1.set.aspect_ratio:{ratio}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling O1", callback_data="bot.kling_o1")
    )

    return builder.as_markup()


def kling_o1_duration_keyboard(current_duration: int = 5) -> InlineKeyboardMarkup:
    """Kling O1 duration selection keyboard (5 or 10 seconds)."""
    builder = InlineKeyboardBuilder()

    durations = [5, 10]

    for duration in durations:
        text = f"✅ {duration} сек" if duration == current_duration else f"{duration} сек"
        builder.row(
            InlineKeyboardButton(text=text, callback_data=f"kling_o1.set.duration:{duration}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling O1", callback_data="bot.kling_o1")
    )

    return builder.as_markup()


def kling_o1_auto_translate_keyboard(current_value: bool = True) -> InlineKeyboardMarkup:
    """Kling O1 auto-translate toggle keyboard."""
    builder = InlineKeyboardBuilder()

    yes_text = "✅ Да" if current_value else "Да"
    no_text = "✅ Нет" if not current_value else "Нет"

    builder.row(
        InlineKeyboardButton(text=yes_text, callback_data="kling_o1.set.auto_translate:yes")
    )
    builder.row(
        InlineKeyboardButton(text=no_text, callback_data="kling_o1.set.auto_translate:no")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к Kling O1", callback_data="bot.kling_o1")
    )

    return builder.as_markup()


# ==============================================
# NANO BANANA 2 KEYBOARDS
# ==============================================

def nano_banana_2_keyboard(current_resolution: str = "2K") -> InlineKeyboardMarkup:
    """Nano Banana 2 main keyboard with resolution and format buttons."""
    builder = InlineKeyboardBuilder()

    # Resolution buttons
    res_2k_text = f"✅ Разрешение – 2К" if current_resolution == "2K" else "Разрешение – 2К"
    res_4k_text = f"✅ Разрешение 4К" if current_resolution == "4K" else "Разрешение 4К"

    builder.row(
        InlineKeyboardButton(text=res_2k_text, callback_data="nb2.set.resolution:2K"),
        InlineKeyboardButton(text=res_4k_text, callback_data="nb2.set.resolution:4K"),
    )

    # Format button
    builder.row(
        InlineKeyboardButton(text="📐 Изменить формат", callback_data="nb2.prms:ratio")
    )

    builder.row(
        InlineKeyboardButton(text="⬅️ В главное меню", callback_data="bot.back")
    )

    return builder.as_markup()


def nano_banana_2_format_keyboard(current_ratio: str = "auto") -> InlineKeyboardMarkup:
    """Nano Banana 2 format (aspect ratio) selection keyboard."""
    builder = InlineKeyboardBuilder()

    ratios = ["1:1", "16:9", "9:16", "3:2", "21:9", "auto"]

    def format_button_text(ratio: str) -> str:
        label = "Авто" if ratio == "auto" else ratio
        return f"✅ {label}" if ratio == current_ratio else label

    builder.row(
        InlineKeyboardButton(text=format_button_text("1:1"), callback_data="nb2.prms.chs:ratio|1:1"),
        InlineKeyboardButton(text=format_button_text("16:9"), callback_data="nb2.prms.chs:ratio|16:9"),
        InlineKeyboardButton(text=format_button_text("9:16"), callback_data="nb2.prms.chs:ratio|9:16"),
    )
    builder.row(
        InlineKeyboardButton(text=format_button_text("3:2"), callback_data="nb2.prms.chs:ratio|3:2"),
        InlineKeyboardButton(text=format_button_text("21:9"), callback_data="nb2.prms.chs:ratio|21:9"),
        InlineKeyboardButton(text=format_button_text("auto"), callback_data="nb2.prms.chs:ratio|auto"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Вернуться в меню", callback_data="bot.nano_banana_2")
    )

    return builder.as_markup()
