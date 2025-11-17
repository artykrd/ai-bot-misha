#!/usr/bin/env python3
# coding: utf-8

"""
Media handlers for video, audio, and image generation.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.keyboards.inline import back_to_main_keyboard
from app.database.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)

router = Router(name="media")


class MediaState(StatesGroup):
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()


# ======================
# VIDEO SERVICES
# ======================

@router.callback_query(F.data == "bot.sora")
async def start_sora(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "**Sora 2 - Video Generation**\n\n"
        "Sora 2 может создавать реалистичные видео длительностью до 20 секунд по вашему описанию.\n\n"
        "Стоимость: ~15,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео, которое вы хотите создать."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="sora")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.luma")
async def start_luma(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Luma Dream Machine\n\n"
        "Luma создаёт качественные видео по вашему описанию.\n\n"
        "Стоимость: ~8,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="luma")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.hailuo")
async def start_hailuo(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Hailuo (MiniMax)\n\n"
        "Hailuo создаёт реалистичные видео.\n\n"
        "Стоимость: ~7,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="hailuo")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.kling")
async def start_kling(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Kling AI\n\n"
        "Kling создаёт высококачественные видео.\n\n"
        "Стоимость: ~9,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.kling_effects")
async def start_kling_effects(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Kling Effects\n\n"
        "Создание видео с эффектами от Kling AI.\n\n"
        "Стоимость: ~10,000 токенов за видео\n\n"
        "Отправьте текстовое описание видео с эффектом."
    )

    await state.set_state(MediaState.waiting_for_video_prompt)
    await state.update_data(service="kling_effects")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# AUDIO SERVICES
# ======================

@router.callback_query(F.data == "bot.suno")
async def start_suno(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Suno AI – Music Generation\n\n"
        "Suno создаёт уникальную музыку и песни по вашему описанию.\n\n"
        "Стоимость: ~5,000 токенов за трек\n\n"
        "Отправьте описание музыки.\n\n"
        "Примеры:\n"
        "- Энергичная рок-композиция\n"
        "- Спокойная джазовая мелодия\n"
        "- Танцевальный электро-трек"
    )

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="suno")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.whisper_tts")
async def start_tts(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "OpenAI TTS – Text to Speech\n\n"
        "Превратите текст в естественную речь.\n\n"
        "Стоимость: ~200 токенов за запрос\n\n"
        "Доступные голоса:\n"
        "- alloy\n- echo\n- fable\n- onyx\n- nova\n- shimmer\n\n"
        "Отправьте текст для озвучки."
    )

    await state.set_state(MediaState.waiting_for_audio_prompt)
    await state.update_data(service="tts")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# IMAGE SERVICES
# ======================

@router.callback_query(F.data == "bot.pi_upscale")
async def start_upscale(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Улучшение качества фото\n\n"
        "Увеличьте разрешение и улучшите качество изображения.\n\n"
        "Стоимость: ~2,000 токенов\n\n"
        "Отправьте изображение."
    )

    await state.set_state(MediaState.waiting_for_upscale_image)
    await state.update_data(service="upscale")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.pi_remb")
async def start_remove_bg(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Удаление фона\n\n"
        "Стоимость: ~500 токенов\n\n"
        "Отправьте изображение для удаления фона."
    )

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="remove_bg")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "bot.pi_repb")
async def start_replace_bg(callback: CallbackQuery, state: FSMContext, user: User):
    text = (
        "Замена фона\n\n"
        "Стоимость: ~500 токенов\n\n"
        "Отправьте изображение, затем укажите цвет фона (white, black, #FF5733)."
    )

    await state.set_state(MediaState.waiting_for_image)
    await state.update_data(service="replace_bg")

    await callback.message.edit_text(text, reply_markup=back_to_main_keyboard())
    await callback.answer()


# ======================
# FSM HANDLERS
# ======================

@router.message(MediaState.waiting_for_video_prompt, F.text)
async def process_video_prompt(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    service_name = data.get("service", "sora")

    display = {
        "sora": "Sora 2",
        "luma": "Luma Dream Machine",
        "hailuo": "Hailuo",
        "kling": "Kling AI",
        "kling_effects": "Kling Effects"
    }.get(service_name, service_name)

    await message.answer(
        f"Функция генерации видео ({display}) находится в разработке.\n"
        f"Ваш запрос получен: {message.text[:100]}..."
    )
    await state.clear()


@router.message(MediaState.waiting_for_audio_prompt, F.text)
async def process_audio_prompt(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    service_name = data.get("service", "suno")

    display = {
        "suno": "Suno AI",
        "tts": "OpenAI TTS"
    }.get(service_name, service_name)

    await message.answer(
        f"Функция генерации аудио ({display}) находится в разработке.\n"
        f"Ваш текст получен: {message.text[:100]}..."
    )
    await state.clear()


@router.message(MediaState.waiting_for_image, F.photo)
async def process_image(message: Message, state: FSMContext, user: User):
    data = await state.get_data()
    service = data.get("service", "remove_bg")

    display = {
        "remove_bg": "Удаление фона",
        "replace_bg": "Замена фона"
    }.get(service, service)

    await message.answer(
        f"Функция обработки изображений ({display}) находится в разработке.\n"
        "Изображение получено!"
    )
    await state.clear()


@router.message(MediaState.waiting_for_upscale_image, F.photo)
async def process_upscale(message: Message, state: FSMContext, user: User):
    await message.answer(
        "Функция улучшения изображения находится в разработке.\n"
        "Изображение получено!"
    )
    await state.clear()
