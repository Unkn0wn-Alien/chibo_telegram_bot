from aiogram import types

from loader import dp, db

from states.menu_uz import Chibo_menu_uz
from states.menu_ru import Chibo_menu_ru

from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru
from keyboards.default_keyboards.confirm_or_delete import con_or_del_uz, con_or_del_ru


@dp.message_handler(text="🛒 Savat")
async def cart(message: types.Message):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if len(cart_products) == 0:
        await message.answer("🤷‍♂️ Savat bo'sh", reply_markup=menu_uz)
    else:
        txt = ""
        sum = 0
        for prod_data in cart_products:
            productname = prod_data["product_name"]
            price = prod_data["price"]
            quantity = prod_data["quantity"]
            text = f"Mahsulot nomi: {productname}\nMahsulot narxi: {price}\nMahsulot soni: {quantity}\n\n"
            sum += price * quantity
            txt += text
        txt += f"Umumiy narxi: {sum} so'm"
        await message.answer(txt, reply_markup=con_or_del_uz)
        await Chibo_menu_uz.con_or_del.set()


@dp.message_handler(text="🛒 Корзина")
async def cart(message: types.Message):
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    if len(cart_products) == 0:
        await message.answer("🤷‍♂️ Корзина пусто", reply_markup=menu_ru)
    else:
        txt = ""
        sum = 0
        for prod_data in cart_products:
            productname = prod_data["productname"]
            price = prod_data["price"]
            quantity = prod_data["quantity"]
            text = f"Название продукта: {productname}\nЦена продукта: {price}\nКоличество продукта: {quantity}\n\n"
            sum += price * quantity
            txt += text
        txt += f"Общая цена: {sum}"
        await message.answer(txt, reply_markup=con_or_del_ru)
        await Chibo_menu_ru.con_or_del.set()