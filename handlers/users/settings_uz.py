from aiogram import types

from loader import dp, db

from aiogram.dispatcher import FSMContext

from states.change_language import Chibo_change_language

from keyboards.default_keyboards.language import markup_change_language_uz, markup_uz_lang
from keyboards.default_keyboards.menu_button_uz import menu_uz
from keyboards.default_keyboards.menu_button_ru import menu_ru


@dp.message_handler(text="⚙ Sozlamalar")
async def settings(message: types.Message):
    await message.answer("Harakatni tanglang 👇", reply_markup=markup_change_language_uz)


@dp.message_handler(text="⬅ Ortga")
async def back_to_menu(message: types.Message):
    await message.answer("Bosh menyu 👇", reply_markup=menu_uz)


@dp.message_handler(text="🌏 Tilni o'zgartirish")
async def change_language(message: types.Message):
    await message.answer("Tilni tanlang 👇", reply_markup=markup_uz_lang)
    await Chibo_change_language.language.set()


@dp.message_handler(state=Chibo_change_language.language, text="⬅ Ortga")
async def back_to_settings(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Harakatni tanglang 👇", reply_markup=markup_change_language_uz)


@dp.message_handler(state=Chibo_change_language.language, text="🇷🇺 Русский")
async def change_to_russia(message: types.Message, state: FSMContext):
    language = message.text.split(" ")[1]
    await db.update_user_language(language_user=language, telegram_id=message.from_user.id)
    await message.answer("Главный меню 👇", reply_markup=menu_ru)
    await state.finish()