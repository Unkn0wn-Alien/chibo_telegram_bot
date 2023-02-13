from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🍴 Menyu")
button_2 = KeyboardButton("📋 Mening buyurtmalarim")
button_3 = KeyboardButton("🛒 Savat")
button_4 = KeyboardButton("✍ Fikr bildirish")
button_5 = KeyboardButton("⚙ Sozlamalar")
button_6 = KeyboardButton("⬅ Ortga")
menu_uz = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1).row(button_2, button_3).row(button_4, button_5)
back_uz = ReplyKeyboardMarkup(resize_keyboard=True).row(button_6)