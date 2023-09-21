from aiogram import Dispatcher
from handlers.text.start import start
from handlers.text.nft_sale import enter_nft_sale_price, send_nft_sale_transaction
from handlers.text.nft_auction import enter_nft_auction_min_bid, enter_nft_auction_max_bid, enter_nft_auction_step_time, enter_nft_auction_step, enter_nft_auction_end_time, send_nft_auction_transaction

def register_text_handler(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])

    # Sale
    dp.register_message_handler(enter_nft_sale_price, state="get_nft_sale_address")
    dp.register_message_handler(send_nft_sale_transaction, state="get_nft_sale_price")

    # Auction
    dp.register_message_handler(enter_nft_auction_min_bid, state="get_nft_auction_address")
    dp.register_message_handler(enter_nft_auction_max_bid, state="get_nft_auction_min_bid")
    dp.register_message_handler(enter_nft_auction_step_time, state="get_nft_auction_max_bid")
    dp.register_message_handler(enter_nft_auction_step, state="get_nft_auction_step_time")
    dp.register_message_handler(enter_nft_auction_end_time, state="get_nft_auction_step")

    dp.register_message_handler(send_nft_auction_transaction, state="nft_auction_end_time")
