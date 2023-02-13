from aiogram import types

from loader import dp, db

from aiogram.dispatcher import FSMContext

from states.change_language import Chibo_change_language

from keyboards.default_keyboards.language import markup_change_language_ru, markup_ru_lang
from keyboards.default_keyboards.menu_button_ru import menu_ru
from keyboards.default_keyboards.menu_button_uz import menu_uz


@dp.message_handler(text="⚙ Настройки")
async def settings(message: types.Message):
    await message.answer("Выберите действие 👇", reply_markup=markup_change_language_ru)


@dp.message_handler(text="⬅ Назад")
async def back_to_menu(message: types.Message):
    await message.answer("Главный меню 👇", reply_markup=menu_ru)


@dp.message_handler(text="🌏 Изменить язык")
async def change_language(message: types.Message):
    await message.answer("Выберите язык 👇", reply_markup=markup_ru_lang)
    await Chibo_change_language.language.set()


@dp.message_handler(state=Chibo_change_language.language, text="⬅ Назад")
async def back_to_settings(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Выберите действие 👇", reply_markup=markup_change_language_ru)


@dp.message_handler(state=Chibo_change_language.language, text="🇺🇿 O'zbek")
async def change_to_russia(message: types.Message, state: FSMContext):
    language = message.text.split(" ")[1]
    await db.update_user_language(language_user=language, telegram_id=message.from_user.id)
    await message.answer("Bosh menyu 👇", reply_markup=menu_uz)
    await state.finish()