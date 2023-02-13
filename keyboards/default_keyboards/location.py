from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

location_uz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Lokatsiyani jo'natish", request_location=True)]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

location_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Отправить локация", request_location=True)]
    ],
    resize_keyboard=True, one_time_keyboard=True
)