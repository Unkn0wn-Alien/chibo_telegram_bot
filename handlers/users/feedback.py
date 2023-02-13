from aiogram import types

from aiogram.dispatcher import FSMContext

from states.feedback import Chibo_feedback

from loader import dp, db

from keyboards.default_keyboards.menu_button_uz import back_uz, menu_uz
from keyboards.default_keyboards.menu_button_ru import back_ru, menu_ru


@dp.message_handler(text="✍ Fikr bildirish")
async def feedback_uz(message: types.Message):
    await message.answer("Fikringizni yozib qoldiring 👇", reply_markup=back_uz)
    await Chibo_feedback.feedback.set()


@dp.message_handler(text="✍ Оставить отзыв")
async def feedback_ru(message: types.Message):
    await message.answer("Оставьте ваш отзыв 👇", reply_markup=back_ru)
    await Chibo_feedback.feedback.set()


@dp.message_handler(state=Chibo_feedback.feedback)
async def back_feedback(message: types.Message, state: FSMContext):
    if message.text == "⬅ Ortga":
        await message.answer("Bosh menyu 👇", reply_markup=menu_uz)
        await state.finish()
    elif message.text == "⬅ Назад":
        await message.answer("Главный меню 👇", reply_markup=menu_ru)
        await state.finish()
    else:
        username = await db.select_username(telegram_id=message.from_user.id)
        await db.add_feedback(name=username["full_name"], feedback=message.text)
        language = await db.select_language(telegram_id=message.from_user.id)
        if language["language"] == "O'zbek":
            await message.answer("Izohingiz uchun rahmat", reply_markup=menu_uz)
            await state.finish()
        elif language["language"] == "Русский":
            await message.answer("Спасибо за ваш отзыв", reply_markup=menu_ru)
            await state.finish()