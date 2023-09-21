from aiogram import Dispatcher
from handlers.text import register_text_handler
from handlers.inline import register_inline_handler


def register_handlers(dp: Dispatcher):
    register_text_handler(dp)
    register_inline_handler(dp)
