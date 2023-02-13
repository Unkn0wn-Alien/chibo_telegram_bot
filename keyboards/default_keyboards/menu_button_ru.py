from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_1 = KeyboardButton("🍴 Меню")
button_2 = KeyboardButton("📋 Мои заказы")
button_3 = KeyboardButton("🛒 Корзина")
button_4 = KeyboardButton("✍ Оставить отзыв")
button_5 = KeyboardButton("⚙ Настройки")
button_6 = KeyboardButton("⬅ Назад")
menu_ru = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1).row(button_2, button_3).row(button_4, button_5)
back_ru = ReplyKeyboardMarkup(resize_keyboard=True).row(button_6)