import re
import asyncpg

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db

from states.start_states import Chibo

from keyboards.default_keyboards.language import markup
from keyboards.default_keyboards.phone_number import phone_number_ru, phone_number_uz
from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru



@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    id = []
    user_ids = await db.select_user_id()
    for user_id in user_ids:
        ids = user_id["telegram_id"]
        id.append(ids)
    if message.from_user.id in id:
        language = await db.select_language(telegram_id=message.from_user.id)
        if language["language"] == "O'zbek":
            await message.answer("Bosh menyu 👇", reply_markup=menu_uz)
        elif language["language"] == "Русский":
            await message.answer("Главное меню 👇", reply_markup=menu_ru)
    else:
        await message.answer("Assalomu aleykum! Botimizga xush kelibsiz!\nIltimos tilni tanlang 👇\n\nЗдравствуйте! Добро пожаловать в наш бот!\nПожалуйста выберите язык 👇", reply_markup=markup)
        await Chibo.choose_language.set()


@dp.message_handler(state=Chibo.choose_language, content_types=types.ContentTypes.TEXT)
async def load_language(message: types.Message, state: FSMContext):
    if message.text == "🇺🇿 O'zbek" or message.text == '🇷🇺 Русский':
        await state.update_data(language=message.text)
        data = await state.get_data()
        language = data.get("language")
        lan = language.split(" ")[1]
        if lan == "O'zbek":
            await message.answer("Ro'yxatdan o'tish uchun telefon raqamingizni kiriting\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring 👇", reply_markup=phone_number_uz)
            await Chibo.phone_number.set()
        elif lan == 'Русский':
            await message.answer("Введите свой номер телефона для регистрации\nОтправьте номер в виде (+998xxxxxxxxx или 998xxxxxxxxx) 👇", reply_markup=phone_number_ru)
            await Chibo.phone_number.set()


@dp.message_handler(state=Chibo.phone_number, content_types=types.ContentTypes.TEXT)
@dp.message_handler(state=Chibo.phone_number, content_types=types.ContentTypes.CONTACT)
async def load_contact_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language")
    lan = language.split(" ")[1]
    match_number = r'''^(\+998|998)(90|91|99|77|94|93|95|97|98|88|33){1}\d{7}$'''
    phone_number = ""
    if message.contact and re.match(match_number, message.contact.phone_number):
        phone_number = message.contact.phone_number
    elif message.text and re.match(match_number, message.text):
        phone_number = message.text
    else:
        if lan == "O'zbek":
            await message.answer("❌ Telefon raqam xato kiritildi\nRaqamni (+998xxxxxxxxx yoki 998xxxxxxxxx) shaklida yuboring 👇")
            return load_language
        elif lan == 'Русский':
            await message.answer("❌ Телефон номер неправильно введен\nОтправьте номер в виде (+998xxxxxxxxx или 998xxxxxxxxx) 👇")
            return load_language
    if phone_number:
        if message.content_type == 'text':
            await state.update_data(contact=phone_number)
            if lan == "O'zbek":
                await message.answer("Iltimos F.I.SH ni kiriting 👇")
                await Chibo.full_name.set()
            elif lan == 'Русский':
                await message.answer("Пожалуйста напишите ваше Ф.И.О 👇")
                await Chibo.full_name.set()
        elif message.content_type == 'contact':
            await state.update_data(contact=phone_number)
            if lan == "O'zbek":
                await message.answer("Iltimos F.I.SH ni kiriting 👇")
                await Chibo.full_name.set()
            elif lan == 'Русский':
                await message.answer("Пожалуйста напишите ваше Ф.И.О 👇")
                await Chibo.full_name.set()


@dp.message_handler(state=Chibo.full_name, content_types=types.ContentTypes.TEXT)
async def load_fullname(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    data = await state.get_data()
    language = data.get("language")
    lan = language.split(" ")[1]
    phone_number = data.get("contact")
    full_name = data.get("full_name")
    try:
        await db.add_user(
            telegram_id=message.from_user.id,
            language=lan,
            phone_number=phone_number,
            full_name=full_name,
            address_id=None
        )
    except asyncpg.exceptions.UniqueViolationError:
        await db.select_user(telegram_id=message.from_user.id)
    if lan == "O'zbek":
        await message.answer("Bosh menyu 👇", reply_markup=menu_uz)
        await state.finish()
    elif lan == "Русский":
        await message.answer("Главное меню 👇", reply_markup=menu_ru)
        await state.finish()