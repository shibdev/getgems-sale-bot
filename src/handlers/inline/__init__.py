from aiogram import Dispatcher
from handlers.inline.start import disconnect, tonkeeper_connect
from handlers.inline.nft_sale import enter_nft_sale_address
from handlers.inline.nft_auction import enter_nft_auction_address
from handlers.inline.menu import menu


def register_inline_handler(dp: Dispatcher):
    dp.register_callback_query_handler(disconnect, text="disconnect")
    
    dp.register_callback_query_handler(enter_nft_sale_address, text="nft_on_sale")

    dp.register_callback_query_handler(enter_nft_auction_address, text="nft_on_auction")

    dp.register_callback_query_handler(menu, text="menu", state="*")

    dp.register_callback_query_handler(tonkeeper_connect, lambda c: c.data.startswith("tonkeeper_button"))
  