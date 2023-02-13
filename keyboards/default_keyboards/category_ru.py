from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

from loader import db

async def category_button_ru():
    category_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    categories = await db.get_categories_ru()
    for category in categories:
        button_text = f"{category['category_name_ru']}"
        category_button.insert(KeyboardButton(text=button_text))
    category_button.insert("⬅ Назадь")
    return category_button


async def product_button_ru(message: types.Message):
    product_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    cat_id = await db.get_categories_by_id_ru(category_name_ru=message.text)
    for i in cat_id:
        products = await db.get_products(i["id"])
        for product in products:
            button_text = f'{product["product_name_ru"]}'
            product_button.insert(KeyboardButton(text=button_text))
    product_button.insert("⬅ Назадь")
    return product_button


button_1 = KeyboardButton("🛒 Добавить в корзину")
button_2 = KeyboardButton("⬅ Назадь")
product_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(button_1, button_2)