from aiogram import types
from aiogram.dispatcher import FSMContext
from db import check_user
from keyboards import connect_buttons, start_menu


async def menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    if not check_user(call.from_user.id):
        await call.message.answer(text="Привет! Выбери через что будем коннектить кошелёк",
                             reply_markup=connect_buttons())
        return

    await call.message.answer((f"Дарова."),
                          reply_markup=start_menu(), disable_web_page_preview=True)
