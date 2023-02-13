from aiogram import types

from loader import dp, db

from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru


@dp.message_handler(text="📋 Mening buyurtmalarim")
async def orders(message: types.Message):
    order_products = await db.select_orders_for_user(telegram_id=message.from_user.id)
    if len(order_products) == 0:
        await message.answer("🤷‍♂️ Sizda buyurtmalar mavjud emas", reply_markup=menu_uz)
    else:
        txt = ""
        sum = 0
        for order_data in order_products:
            product_name = order_data["product_name"]
            price = order_data["price"]
            quantity = order_data["quantity"]
            phone_number = order_data["phone_number"]
            time = order_data["created_at"]
            order_code = order_data["order_code"]
            text = f"Buyurtma kodi: {order_code}\nMahsulot nomi: {product_name}\nMahsulot narxi: {price}\nMahsulot soni: {quantity}\nTelefon raqamingiz: {phone_number}\nBuyurtma berilgan vaqt: {time}\n\n"
            sum += price * quantity
            txt += text
        txt += f"Umumiy narxi: {sum} so'm"
        await message.answer(txt, reply_markup=menu_uz)


@dp.message_handler(text="📋 Мои заказы")
async def orders(message: types.Message):
    order_products = await db.select_orders_for_user(telegram_id=message.from_user.id)
    if len(order_products) == 0:
        await message.answer("🤷‍♂️ У вас нет заказы", reply_markup=menu_ru)
    else:
        txt = ""
        sum = 0
        for order_data in order_products:
            product_name = order_data["product_name"]
            price = order_data["price"]
            quantity = order_data["quantity"]
            phone_number = order_data["phone_number"]
            time = order_data["created_at"]
            order_code = order_data["order_code"]
            text = f"Код покупка: {order_code}\nНазвание продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {quantity}\nВаш телефон номер: {phone_number}\nВремя заказа: {time}\n\n"
            sum += price * quantity
            txt += text
        txt += f"Общая цена: {sum} сум"
        await message.answer(txt, reply_markup=menu_ru)