import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from handlers import register_handlers
from config import BOT_TOKEN


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="start")
    ]
    await bot.set_my_commands(commands)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

async def bot_polling():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Starting bot")

    memory = MemoryStorage()
    dp = Dispatcher(bot, storage=memory)

    register_handlers(dp)

    await set_commands(bot)

    try:
        await dp.skip_updates()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot_polling())
    loop.run_forever()
