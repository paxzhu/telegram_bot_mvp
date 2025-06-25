from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_instagram = State()
    waiting_for_memory = State()

__all__ = ["Form"]