"""
Admin bot FSM states.
"""
from aiogram.fsm.state import State, StatesGroup


class CreateUnlimitedLink(StatesGroup):
    """States for creating unlimited invite link."""
    waiting_for_days = State()
    waiting_for_max_uses = State()
    waiting_for_description = State()


class GiveTokens(StatesGroup):
    """States for giving tokens to user."""
    waiting_for_user_id = State()
    waiting_for_amount = State()


class BanUser(StatesGroup):
    """States for banning user."""
    waiting_for_user_id = State()
    waiting_for_reason = State()


class UnbanUser(StatesGroup):
    """States for unbanning user."""
    waiting_for_user_id = State()


class CreatePromo(StatesGroup):
    """States for creating promocode."""
    waiting_for_code = State()
    waiting_for_tokens = State()


class Broadcast(StatesGroup):
    """States for broadcast message."""
    waiting_for_message = State()
