from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_instagram = State()
    waiting_for_memory = State()

class IntroFlow(StatesGroup):
    asking_name = State()
    asking_memory = State()
    waiting_image = State()
    collecting_details = State()

__all__ = ["Form", "IntroFlow"]