from aiogram import types
import asyncio
from pytonconnect import TonConnect
from pytonconnect.storage import FileStorage
from tonsdk.utils import Address
from keyboards import start_menu
from db import check_user, check_address, add_user, delete_user
import qrcode
from config import CONNECT_URL
import os

async def disconnect(call: types.CallbackQuery):
    if check_user(call.from_user.id):
        delete_user(call.from_user.id)
        os.remove(f"connections/{call.from_user.id}.json")
        await call.answer("Удалено!")


async def tonkeeper_connect(call: types.CallbackQuery):
    if check_user(call.from_user.id):
        return

    storage = FileStorage(f"connections/{call.from_user.id}.json")
    connector = TonConnect(CONNECT_URL, storage)

    is_connected = await connector.restore_connection()
    print('is_connected:', is_connected)

    def status_changed(wallet_info):
        print('wallet_info:', wallet_info)
        unsubscribe()

    def status_error(e):
        print('connect_error:', e)

    unsubscribe = connector.on_status_change(status_changed, status_error)
    
    try:
        url = await connector.connect(connector.get_wallets()[0])
    except:
        await connector.disconnect()
        url = await connector.connect(connector.get_wallets()[0])
    qrcode.make(url).save("images/qrcode.png")
    
    await call.bot.send_photo(call.from_user.id,
                              photo=open("images/qrcode.png", "rb"),
                              caption=f"Воспользуйся <a href='{url}'>этой ссылкой</a> для подключения или qr-кодом сверху")
    
    address = None
    for i in range(120):
        await asyncio.sleep(1)
        if connector.connected:
            if connector.account.address:
                address = Address(connector.account.address).to_string(1, 1, 1)
            break
    
    if not address:
        return

    if check_address(address):
        return
    
    add_user(call.from_user.id, address)
    await call.message.answer(text=f"Подключено!")

    await call.message.answer((f"Дарова."),
                              reply_markup=start_menu(), disable_web_page_preview=True)
