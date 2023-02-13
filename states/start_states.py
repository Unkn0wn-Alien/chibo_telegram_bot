from aiogram.dispatcher.filters.state import State, StatesGroup

class Chibo(StatesGroup):
    choose_language = State()
    phone_number = State()
    full_name = State()