from aiogram.fsm.state import State, StatesGroup

class LocationState(StatesGroup):
    choosing_country = State()