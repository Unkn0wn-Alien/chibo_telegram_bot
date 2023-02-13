from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

from loader import db

async def category_button_uz():
    category_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    categories = await db.get_categories_uz()
    for category in categories:
        button_text = f"{category['category_name_uz']}"
        category_button.insert(KeyboardButton(text=button_text))
    category_button.insert("⬅ Ortga")
    return category_button


async def product_button_uz(message: types.Message):
    product_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    cat_id = await db.get_categories_by_id_uz(category_name_uz=message.text)
    for i in cat_id:
        products = await db.get_products(i["id"])
        for product in products:
            button_text = f'{product["product_name_uz"]}'
            product_button.insert(KeyboardButton(text=button_text))
    product_button.insert("⬅ Ortga")
    return product_button