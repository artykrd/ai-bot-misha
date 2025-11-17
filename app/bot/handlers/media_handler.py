"""
Media handlers for video, audio, and image generation.
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.keyboards.inline import back_to_main_keyboard
from app.database.models.user import User
from app.services.video.sora_service import SoraService
from app.services.video.luma_service import LumaService
from app.services.video.replicate_service import ReplicateService
from app.services.audio.suno_service import SunoService
from app.services.audio.openai_audio_service import OpenAIAudioService
from app.services.image.removebg_service import RemoveBgService
from app.services.image.stability_service import StabilityService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="media")


class MediaState(StatesGroup):
    """States for media generation."""
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()


@router.callback_query(F.data == "bot.sora")
async def start_sora(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Sora video generation."""
    text = """☁️ **Sora 2 – Video Generation**

🎬 Sora 2 может создавать реалистичные видео длительностью до 20 секунд по вашему описанию.

**Стоимость:** ~15,000 токенов за видео

📝 Отправьте текстовое описание видео, которое вы хотите создать."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="sora")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()



@router.callback_query(F.data == "bot.luma")
async def start_luma(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Luma video generation."""
    text = """📹 **Luma Dream Machine**

🎬 Luma создаёт качественные видео по вашему описанию.

**Стоимость:** ~8,000 токенов за видео

📝 Отправьте текстовое описание видео."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="luma")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.hailuo")
async def start_hailuo(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Hailuo video generation."""
    text = """🎥 **Hailuo (MiniMax)**

🎬 Hailuo создаёт реалистичные видео.

**Стоимость:** ~7,000 токенов за видео

📝 Отправьте текстовое описание видео."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="hailuo")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.kling")
async def start_kling(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling video generation."""
    text = """🎞 **Kling AI**

🎬 Kling создаёт высококачественные видео.

**Стоимость:** ~9,000 токенов за видео

📝 Отправьте текстовое описание видео."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.kling_effects")
async def start_kling_effects(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Kling Effects video generation."""
    text = """🧙 **Kling Effects**

🎬 Создание видео с эффектами от Kling AI.

**Стоимость:** ~10,000 токенов за видео

📝 Отправьте текстовое описание видео с эффектом."""

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling_effects")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.suno")
async def start_suno(callback: CallbackQuery, state: FSMContext, user: User):
    """Start Suno music generation."""
    text = """🎧 **Suno AI – Music Generation**

🎵 Suno создаёт уникальную музыку и песни по вашему описанию.

**Стоимость:** ~5,000 токенов за трек

📝 Отправьте описание музыки, которую хотите создать.

**Примеры:**
- "Энергичная рок-композиция с гитарой"
- "Спокойная джазовая мелодия для вечера"
- "Танцевальный электро трек"""

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="suno")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()



@router.callback_query(F.data == "bot.whisper_tts")
async def start_tts(callback: CallbackQuery, state: FSMContext, user: User):
    """Start OpenAI TTS."""
    text = """🗣 **OpenAI TTS – Text to Speech**

🎙 Превратите текст в естественную речь.

**Стоимость:** ~200 токенов за запрос

**Доступные голоса:**
- alloy (нейтральный)
- echo (мужской)
- fable (выразительный)
- onyx (глубокий)
- nova (женский)
- shimmer (мягкий)

📝 Отправьте текст для озвучки."""

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="tts")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.pi_upscale")
async def start_upscale(callback: CallbackQuery, state: FSMContext, user: User):
    """Start image upscaling."""
    text = """🔎 **Улучшение качества фото**

✨ Увеличьте разрешение и улучшите качество вашего изображения.

**Стоимость:** ~2,000 токенов за изображение

📸 Отправьте изображение для улучшения."""

    await state.set_state(MediaState.waiting_for_upscale_image)
    await state.update_data(service="upscale")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.pi_remb")
async def start_remove_bg(callback: CallbackQuery, state: FSMContext, user: User):
    """Start background removal."""
    text = """🪞 **Удаление фона**

✂️ Удалите фон с вашего изображения.

**Стоимость:** ~500 токенов за изображение

📸 Отправьте изображение для удаления фона."""

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="remove_bg")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "bot.pi_repb")
async def start_replace_bg(callback: CallbackQuery, state: FSMContext, user: User):
    """Start background replacement."""
    text = """🪄 **Замена фона**

🎨 Удалите старый фон и замените его на новый цвет.

**Стоимость:** ~500 токенов за изображение

📸 Отправьте изображение для замены фона.
После отправки укажите цвет (например: white, black, #FF5733)."""

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="replace_bg")

    await callback.message.edit_text(
        text,
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()


        "bot.gpt_image": "GPT Image",
        "bot.midjourney": "Midjourney",
        "bot_stable_diffusion": "Stable Diffusion",
        "bot.recraft": "Recraft",
        "bot.faceswap": "FaceSwap"
    }
    service = service_names.get(callback.data, "Сервис")

    await callback.answer(
        f"⚠️ {service} будет доступен в следующей версии",
        show_alert=True
    )

