import asyncpg
import re

from datetime import datetime
from aiogram import types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import dp, db, bot

from config.config import ADMINS

from aiogram.dispatcher import FSMContext
from states.menu_ru import Chibo_menu_ru

from keyboards.default_keyboards.menu_button_ru import menu_ru, back_ru
from keyboards.default_keyboards.yes_or_no import yes_or_no_ru
from keyboards.default_keyboards.confirm_or_delete import con_or_del_ru
from keyboards.default_keyboards.phone_number import phone_number_ru
from keyboards.default_keyboards.location import location_ru
from keyboards.default_keyboards.category_ru import category_button_ru, product_button_ru


@dp.message_handler(text="🍴 Меню")
async def menu(message: types.Message):
    c_b_u = await category_button_ru()
    await message.answer("Что вы собираетесь заказать?\n👇👇👇", reply_markup=c_b_u)
    await Chibo_menu_ru.categories.set()


@dp.message_handler(state=Chibo_menu_ru.categories, content_types=types.ContentTypes.TEXT)
async def categories(message: types.Message, state: FSMContext):
    if message.text == "⬅ Назад":
        await state.finish()
        await message.answer("Главное меню\n👇", reply_markup=menu_ru)
    else:
        await state.update_data(category=message.text)
        p_b_u = await product_button_ru(message)
        await message.answer("Выберите продукта\n👇", reply_markup=p_b_u)
        await Chibo_menu_ru.products.set()


@dp.message_handler(state=Chibo_menu_ru.products, content_types=types.ContentTypes.TEXT)
async def products(message: types.Message, state: FSMContext):
    if message.text == "⬅ Назад":
        c_b_u = await category_button_ru()
        await message.answer("Что вы собираетесь заказать?\n👇👇👇", reply_markup=c_b_u)
        await Chibo_menu_ru.previous()
    else:
        await state.update_data(product=message.text)
        data = await state.get_data()
        product = data.get("product")
        product_data = await db.get_product_by_id_ru(product_name_ru=product)
        for i in product_data:
            product_id = await db.get_product(i["id"])
            photo = open(product_id["photo"], "rb")
            await message.answer_photo(photo=photo, caption=f'Название: {product_id["product_name_ru"]}\nСостав: {product_id["description_ru"]}\n\nЦена: {product_id["price"]} сум', reply_markup=get_keyboard_ru(1))
        await Chibo_menu_ru.show_product.set()


counter = 1

def get_keyboard_ru(counter):
    ikb = types.InlineKeyboardMarkup(row_width=4)
    button_plyus = types.InlineKeyboardButton('➕', callback_data='plyus')
    button_sonii = types.InlineKeyboardButton(f'{counter} шт', callback_data='1')
    button_minuss = types.InlineKeyboardButton('➖', callback_data='minuss')
    button_savat_ru = types.InlineKeyboardButton("🛒 Добавит в корзину", callback_data='savat_ru')
    backru = types.InlineKeyboardButton("⬅ Назад", callback_data="backru")
    ikb.add(button_minuss, button_sonii, button_plyus).add(button_savat_ru).add(backru)
    return ikb


@dp.callback_query_handler(state=Chibo_menu_ru.show_product)
async def product_total(callback: types.CallbackQuery, state: FSMContext):
    global counter
    if callback.data == "plyus":
        counter += 1
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=get_keyboard_ru(counter))
    elif callback.data == "minuss":
        if counter >= 2:
            counter -= 1
            await bot.edit_message_reply_markup(chat_id=callback.from_user.id, message_id=callback.message.message_id, reply_markup=get_keyboard_ru(counter))
    elif callback.data == "backru":
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        product_button = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        data = await state.get_data()
        category_name = data.get("category")
        cat_id = await db.get_categories_by_id_ru(category_name_ru=category_name)
        for i in cat_id:
            products = await db.get_products(i["id"])
            for product in products:
                button_text = f'{product["product_name_ru"]}'
                product_button.insert(KeyboardButton(text=button_text))
        product_button.insert("⬅ Назад")
        await callback.message.answer("Выберите продукта\n👇", reply_markup=product_button)
        await Chibo_menu_ru.products.set()
    elif callback.data == "savat_ru":
        data = await state.get_data()
        product_name = data.get("product")
        product_id = await db.get_product_by_id_ru(product_name_ru=product_name)
        for i in product_id:
            product_data = await db.get_product(i["id"])
            prod_id = product_data["id"]
            price = product_data["price"]
            if_exist = await db.select_cart_if_exist(product_id=prod_id, telegram_id=callback.from_user.id)
            if if_exist is not None:
                await db.update_product_quantity(product_id=prod_id, count=int(counter), telegram_id=callback.from_user.id)
            try:
                await db.add_cart(
                    product_id=prod_id,
                    product_name=product_name,
                    price=price,
                    count=int(counter),
                    telegram_id=callback.from_user.id
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=callback.from_user.id)
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        await callback.message.answer("🔄 Ещё выбираете продукт?\n👇", reply_markup=yes_or_no_ru)
        await Chibo_menu_ru.yes_or_no.set()


@dp.message_handler(state=Chibo_menu_ru.yes_or_no, content_types=types.ContentTypes.TEXT)
async def message_yes(message: types.Message, state: FSMContext):
    await state.update_data(yes_or_no=message.text)
    if message.text == "✅ Да":
        c_b_u = await category_button_ru()
        await message.answer("Что вы собираетесь заказать?\n👇👇👇", reply_markup=c_b_u)
        await Chibo_menu_ru.categories.set()
    elif message.text == "❌ Нет":
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        txt = ""
        sum = 0
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            quantity = prod_data["quantity"]
            text = f"Название продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {quantity}\n\n"
            sum += price * quantity
            txt += text
        txt += f"Общая цена: {sum} сум"
        await message.answer(txt, reply_markup=con_or_del_ru)
        await Chibo_menu_ru.con_or_del.set()


@dp.message_handler(state=Chibo_menu_ru.con_or_del, content_types=types.ContentTypes.TEXT)
async def con_or_del(message: types.Message, state: FSMContext):
    await state.update_data(con_or_del=message.text)
    if message.text == "🏠 Главное меню":
        await state.finish()
        await message.answer("Главное меню 👇", reply_markup=menu_ru)
    elif message.text == "❌ Отказать":
        await state.finish()
        await db.delete_cart(telegram_id=message.from_user.id)
        await message.answer("Товары из корзины были удалены 👇", reply_markup=menu_ru)
    elif message.text == "✅ Подтверждение":
        phone_number = await db.select_phone_number(telegram_id=message.from_user.id)
        await message.answer(f"Хотите разместить заказ с этим\n{phone_number['phone_number']}\nномером телефона? 👇", reply_markup=yes_or_no_ru)
        await Chibo_menu_ru.phone_number_order_confirm.set()


@dp.message_handler(state=Chibo_menu_ru.phone_number_order_confirm, content_types=types.ContentTypes.TEXT)
async def new_phone_number_confirm(message: types.Message, state: FSMContext):
    await state.update_data(yes_or_no_phone_number=message.text)
    data = await state.get_data()
    yes_or_no_phone_number = data.get("yes_or_no_phone_number")
    if yes_or_no_phone_number == "❌ Нет":
        await message.answer("Введите новый номер телефона\nОтправьте номер в виде (+998xxxxxxxx или 998xxxxxxxxx) 👇", reply_markup=phone_number_ru)
        await Chibo_menu_ru.new_phone_number.set()
    elif yes_or_no_phone_number == "✅ Да":
        await message.answer("Отправьте свой адрес 👇", reply_markup=location_ru)
        await Chibo_menu_ru.address.set()


@dp.message_handler(state=Chibo_menu_ru.new_phone_number, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=Chibo_menu_ru.new_phone_number, content_types=types.ContentTypes.CONTACT)
async def new_phone_number(message: types.Message, state: FSMContext):
    language = await db.select_language(telegram_id=message.from_user.id)
    match_number = r'''^(\+998|998)(90|91|99|77|94|93|95|97|98|88|33){1}\d{7}$'''
    phone_number = ""
    if message.contact and re.match(match_number, message.contact.phone_number):
        phone_number = message.contact.phone_number
    elif message.text and re.match(match_number, message.text):
        phone_number = message.text
    else:
        if language["language"] == "Русский":
            await message.answer("❌ Телефон номер введен неправильно\nОтправьте номер в виде (+998xxxxxxxx или 998xxxxxxxxx) 👇", reply_markup=phone_number_ru)
            return new_phone_number_confirm
    if phone_number:
        if message.content_type == 'text':
            await state.update_data(new_phone_number=phone_number)
            data = await state.get_data()
            new_phone_number = data.get("new_phone_number")
            await db.update_user_phone_number(phone_number=new_phone_number, telegram_id=message.from_user.id)
            await message.answer("Отправьте свой адрес 👇", reply_markup=location_ru)
            await Chibo_menu_ru.address.set()
        elif message.content_type == 'contact':
            await state.update_data(new_phone_number=phone_number)
            data = await state.get_data()
            new_phone_number = data.get("new_phone_number")
            await db.update_user_phone_number(phone_number=new_phone_number, telegram_id=message.from_user.id)
            await message.answer("Отправьте свой адрес 👇", reply_markup=location_ru)
            await Chibo_menu_ru.address.set()


@dp.message_handler(state=Chibo_menu_ru.address, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=Chibo_menu_ru.address, content_types=types.ContentTypes.LOCATION)
async def load_address(message: types.Message, state: FSMContext):
    if message.content_type == "text":
        await state.update_data(address=message.text)
        data = await state.get_data()
        cart_products = await db.select_cart(telegram_id=message.from_user.id)
        ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
        phone_number = ph_number["phone_number"]
        address = data.get("address")
        order_code = datetime.now().strftime('%d%m%Y%H%M%S')
        try:
            await db.add_address(
                address=address,
                long=None,
                lat=None,
                telegram_id=message.from_user.id
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        try:
            await db.add_order(
                order_code=order_code,
                telegram_id=message.from_user.id
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        order_id = 0
        order_data = await db.select_order_by_id(telegram_id=message.from_user.id)
        for order_id in order_data:
            order_id = order_id["id"]
        for i in cart_products:
            product_id = i["product_id"]
            quantity = i["quantity"]
            try:
                await db.add_order_details(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
        for prod_data in cart_products:
            product_name = prod_data["product_name"]
            price = prod_data["price"]
            quantity = prod_data["quantity"]
            product_id = prod_data["product_id"]
            try:
                await db.add_order_ontime(
                    product_name=product_name,
                    order_code=order_code,
                    price=price,
                    quantity=quantity,
                    telegram_id=message.from_user.id,
                    phone_number=phone_number,
                    product_id=product_id
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
        order_products = await db.select_order_ontime(telegram_id=message.from_user.id)
        txt = ""
        txt_admin = ""
        sum = 0
        for order_data in order_products:
            product_name = order_data["product_name"]
            price = order_data["price"]
            quantity = order_data["quantity"]
            phone_number = order_data["phone_number"]
            order_code = order_data["order_code"]
            try:
                await db.add_orders_for_user(
                    order_code=order_code,
                    product_name=product_name,
                    price=price,
                    quantity=quantity,
                    telegram_id=message.from_user.id,
                    phone_number=phone_number
                )
            except asyncpg.exceptions.UniqueViolationError:
                await db.select_user(telegram_id=message.from_user.id)
            text = f"Название продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {quantity}\n\n"
            text_admin = f"Название продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {quantity}\n\n"
            sum += price * quantity
            txt += text
            txt_admin += text_admin
        txt += f"Ваш номер телефона: {phone_number}\nВаш адрес: {address}\nВремя заказа: {order_data['created_at']}\nКод покупка: {order_code}\n\n"
        txt += f"Общая цена: {sum} сум"
        txt_admin += f"Телефон номер клиента: {phone_number}\nАдрес клиента: {address}\nВремя заказа: {order_data['created_at']}\nКод покупка: {order_code}\n\n"
        txt_admin += f"Общая цена: {sum} сум"
        await message.answer(txt)
        await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
        await message.answer("Ваш заказ принято\nСкоро свяжутся с вами", reply_markup=menu_ru)
        await db.delete_cart(telegram_id=message.from_user.id)
        await db.delete_order_ontime(telegram_id=message.from_user.id)
        await state.finish()
    if message.content_type == "location":
        await state.update_data(location=message.location)
        data = await state.get_data()
        location = data.get("location")
        try:
            await db.add_address(
                address=None,
                long=str(location["longitude"]),
                lat=str(location["latitude"]),
                telegram_id=message.from_user.id
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        await message.answer("Оставляйте комментарии к заказу и адресу 👇👇👇\n\nНапример: дом, номер квартиры, ориентир, а также пожелания к заказу")
        await Chibo_menu_ru.real_adress.set()


@dp.message_handler(state=Chibo_menu_ru.real_adress, content_types=types.ContentTypes.TEXT)
async def real_feedback(message: types.Message, state: FSMContext):
    await state.update_data(order_feedback=message.text)
    data = await state.get_data()
    location = data.get("location")
    order_feedback = data.get("order_feedback")
    cart_products = await db.select_cart(telegram_id=message.from_user.id)
    ph_number = await db.select_phone_number(telegram_id=message.from_user.id)
    phone_number = ph_number["phone_number"]
    order_code = datetime.now().strftime('%d%m%Y%H%M%S')
    try:
        await db.add_order(
            order_code=order_code,
            telegram_id=message.from_user.id
        )
    except asyncpg.exceptions.UniqueViolationError:
        await db.select_user(telegram_id=message.from_user.id)
    order_id = 0
    order_data = await db.select_order_by_id(telegram_id=message.from_user.id)
    for order_id in order_data:
        order_id = order_id["id"]
    for i in cart_products:
        product_id = i["product_id"]
        quantity = i["quantity"]
        try:
            await db.add_order_details(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
    for prod_data in cart_products:
        product_name = prod_data["product_name"]
        price = prod_data["price"]
        quantity = prod_data["quantity"]
        product_id = prod_data["product_id"]
        try:
            await db.add_order_ontime(
                product_name=product_name,
                order_code=order_code,
                price=price,
                quantity=quantity,
                telegram_id=message.from_user.id,
                phone_number=phone_number,
                product_id=product_id
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
    order_products = await db.select_order_ontime(telegram_id=message.from_user.id)
    txt = ""
    txt_admin = ""
    sum = 0
    for order_data in order_products:
        product_name = order_data["product_name"]
        price = order_data["price"]
        quantity = order_data["quantity"]
        phone_number = order_data["phone_number"]
        order_code = order_data["order_code"]
        try:
            await db.add_orders_for_user(
                order_code=order_code,
                product_name=product_name,
                price=price,
                quantity=quantity,
                telegram_id=message.from_user.id,
                phone_number=phone_number
            )
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(telegram_id=message.from_user.id)
        text = f"Название продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {quantity}\n\n"
        text_admin = f"Название продукта: {product_name}\nЦена продукта: {price}\nКоличество продукта: {quantity}\n\n"
        sum += price * quantity
        txt += text
        txt_admin += text_admin
    txt += f"Ваш номер телефона: {phone_number}\nВремя заказа: {order_data['created_at']}\nКомментарий к заказу: {order_feedback}\nКод покупка: {order_code}\n\n"
    txt += f"Общая цена: {sum} сум"
    txt_admin += f"Телефон номер клиента: {phone_number}\nВремя заказа: {order_data['created_at']}\nКомментарий к заказу: {order_feedback}\nКод покупка: {order_code}\n\n"
    txt_admin += f"Общая цена: {sum} сум"
    await message.answer(txt)
    await bot.send_message(chat_id=ADMINS[0], text=txt_admin)
    await bot.send_location(chat_id=ADMINS[0], longitude=location["longitude"], latitude=location["latitude"])
    await message.answer("Ваш заказ принято\nСкоро свяжутся с вами", reply_markup=menu_ru)
    await db.delete_cart(telegram_id=message.from_user.id)
    await db.delete_order_ontime(telegram_id=message.from_user.id)
    await state.finish()