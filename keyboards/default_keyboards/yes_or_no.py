from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("✅ Ha")
button_2 = KeyboardButton("✅ Да")
button_3 = KeyboardButton("❌ Yo'q")
button_4 = KeyboardButton("❌ Нет")
yes_or_no_uz = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_3)
yes_or_no_ru = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_2, button_4)