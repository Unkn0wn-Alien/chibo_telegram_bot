from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("✅ Tasdiqlash")
button_2 = KeyboardButton("✅ Подтверждение")
button_3 = KeyboardButton("❌ Bekor qilish")
button_4 = KeyboardButton("❌ Отказать")
button_5 = KeyboardButton(text="🏠 Bosh menyu")
button_6 = KeyboardButton(text="🏠 Главное меню")
con_or_del_uz = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_3).row(button_5)
con_or_del_ru = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_2, button_4).row(button_6)