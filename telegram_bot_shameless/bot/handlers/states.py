from aiogram.dispatcher.filters.state import State, StatesGroup

class SpecificShift(StatesGroup):
    waiting_date = State()
    confirming_date = State()
    waiting_position = State()
    confirming_position = State()
    waiting_shift_size = State()
    confirming_shift_size = State()
    conditions_selected = State()
