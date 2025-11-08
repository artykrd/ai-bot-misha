"""
FSM States for dialogs.
"""
from aiogram.fsm.state import State, StatesGroup


class DialogStates(StatesGroup):
    """States for dialog management."""
    waiting_for_message = State()
    creating_dialog = State()
    selecting_model = State()
    setting_system_prompt = State()


class PaymentStates(StatesGroup):
    """States for payment process."""
    waiting_for_payment = State()
    processing_payment = State()


class PromocodeStates(StatesGroup):
    """States for promocode activation."""
    waiting_for_code = State()


class AIGenerationStates(StatesGroup):
    """States for AI content generation."""
    waiting_for_prompt = State()
    waiting_for_image = State()
    processing = State()
