from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def menu():
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text="Меню", callback_data="menu"))

def approve_transaction():
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text="✅ Подтвердить", url="https://app.tonkeeper.com/ton-connect"))
