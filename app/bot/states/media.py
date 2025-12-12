"""
FSM States for media generation (video, audio, image).
"""
from aiogram.fsm.state import State, StatesGroup


class MediaState(StatesGroup):
    """States for media generation."""
    waiting_for_video_prompt = State()
    waiting_for_audio_prompt = State()
    waiting_for_image_prompt = State()
    waiting_for_image = State()
    waiting_for_upscale_image = State()
    waiting_for_whisper_audio = State()
    waiting_for_vision_image = State()
    waiting_for_vision_prompt = State()
    # Photo tools states
    waiting_for_photo_upscale = State()
    waiting_for_photo_replace_bg = State()
    waiting_for_photo_remove_bg = State()
    waiting_for_photo_vectorize = State()
    # Smart input handling states
    waiting_for_photo_action_choice = State()  # User sent photo, need to choose what to do
