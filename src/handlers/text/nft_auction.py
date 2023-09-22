from aiogram import types
from aiogram.dispatcher import FSMContext
from pytonconnect import TonConnect
from pytonconnect.storage import FileStorage
from pytonconnect.exceptions import UserRejectsError
from keyboards import start_menu, approve_transaction, menu
from db import get_user_address
from config import CONNECT_URL
import time
from tonsdk.boc import begin_cell
from tonsdk.utils import Address, bytes_to_b64str
from tonsdk.utils._exceptions import InvalidAddressError
from contracts import AuctionContract
from itertools import zip_longest


async def enter_nft_auction_min_bid(message: types.Message, state: FSMContext):
    await state.update_data(nft_address=message.text.split("\n"))
    await message.answer("Введите минимальную ставку NFT",
                         reply_markup=menu())
    await state.set_state("get_nft_auction_min_bid")

async def enter_nft_auction_max_bid(message: types.Message, state: FSMContext):
    await state.update_data(nft_min_bid=message.text.split("\n"))
    await message.answer("Введите максимальную ставку NFT(0 - без максимальной ставки)",
                         reply_markup=menu())
    await state.set_state("get_nft_auction_max_bid")

async def enter_nft_auction_step_time(message: types.Message, state: FSMContext):
    await state.update_data(nft_max_bid=message.text.split("\n"))
    await message.answer("На сколько будет продливаться аукцион после новой ставки?(рекомендуется 1 час) Введите часы/дни/месяцы. Примеры: 15m(15 минут), 12h(12 часов), 7d(7 дней)",
                         reply_markup=menu())
    await state.set_state("get_nft_auction_step_time")


async def enter_nft_auction_step(message: types.Message, state: FSMContext):
    await state.update_data(nft_step_time=message.text.split("\n"))
    await message.answer("Введите минимальный шаг ставки в процентах",
                         reply_markup=menu())
    await state.set_state("get_nft_auction_step")

async def enter_nft_auction_end_time(message: types.Message, state: FSMContext):
    await state.update_data(nft_step=message.text.split("\n"))
    await message.answer("Введите часы/дни/месяцы до конца аукциона",
                         reply_markup=menu())
    await state.set_state("nft_auction_end_time")


async def send_nft_auction_transaction(message: types.Message, state: FSMContext):
    try:
        storage = FileStorage(f"connections/{message.from_user.id}.json")
        connector = TonConnect(CONNECT_URL, storage)

        is_connected = await connector.restore_connection()
        if not is_connected:
            print("Not connected")
            return

        transaction = {
            "valid_until": (int(time.time()) + 900) * 1000,
            "messages": []
        }

        nft_auction_end_time = message.text.split("\n")

        seconds_per_unit = {
            "m": 60,
            "h": 60 * 60,
            "d": 24 * 60 * 60
        }

        data = await state.get_data()
        user_address = Address(get_user_address(message.from_user.id))

        # Тут заполняется онли nft_min_bid, осторожно
        for nft_address, nft_min_bid, nft_max_bid, nft_step, nft_step_time, nft_end_time in zip_longest(data["nft_address"], data["nft_min_bid"], data["nft_max_bid"], data["nft_step"], data["nft_step_time"], nft_auction_end_time, fillvalue=float(data["nft_min_bid"][-1])):
            fees_cell = begin_cell()\
                        .store_address(user_address)\
                        .store_uint(0, 32)\
                        .store_uint(0, 32)\
                        .store_address(user_address)\
                        .store_uint(0, 32)\
                        .store_uint(0, 32)\
                        .end_cell()\
            
            constant_cell = begin_cell()\
                            .store_int(0, 32)\
                            .store_address(user_address)\
                            .store_coins(int(float(nft_min_bid) * 1e9))\
                            .store_coins(int(float(nft_max_bid) * 1e9))\
                            .store_coins(nft_step)\
                            .store_uint(int(int(nft_step_time[:-1]) * seconds_per_unit.get(nft_step_time[-1], 60*60)), 32)\
                            .store_address(Address(nft_address))\
                            .store_uint(int(time.time()), 32)\
                            .end_cell()

            auction_data_cell = begin_cell()\
                            .store_int(0, 1)\
                            .store_int(0, 1)\
                            .store_int(0, 1)\
                            .store_address(None)\
                            .store_coins(0)\
                            .store_uint(0, 32)\
                            .store_uint(int(int(nft_end_time[:-1]) * seconds_per_unit.get(nft_end_time[-1], 60*60) + time.time()), 32)\
                            .store_address(user_address)\
                            .store_ref(fees_cell)\
                            .store_ref(constant_cell)\
                            .store_bit(0)\
                            .end_cell()\
            
            auction_contract = AuctionContract(
                data_cell=auction_data_cell
            )

            auction_body = begin_cell()\
                        .store_uint(1, 32)\
                        .store_uint(0, 64)\
                        .end_cell()
                            
            nft_transfer_cell = begin_cell()\
                                    .store_uint(0x5fcc3d14, 32)\
                                    .store_uint(0, 64)\
                                    .store_address(Address("EQAIFunALREOeQ99syMbO6sSzM_Fa1RsPD5TBoS0qVeKQ-AR"))\
                                    .store_address(user_address)\
                                    .store_bit(0)\
                                    .store_coins(int(0.25*1e9))\
                                    .store_bit(0)\
                                    .store_uint(0x0fe0ede, 31)\
                                    .store_ref(auction_contract.create_state_init()["state_init"])\
                                    .store_ref(auction_body)\
                                    .end_cell()

            transaction["messages"].append(
                {
                    "address": nft_address,
                    "amount": str(int(0.35*1e9)),
                    "payload": bytes_to_b64str(nft_transfer_cell.to_boc(False))
                }
            )
        await message.answer("Теперь подтверди транзакцию",
                            reply_markup=approve_transaction())
          
        try:
            result = await connector.send_transaction(transaction)
            nft_links = '\n'.join('https://getgems.io/nft/' + i for i in data['nft_address'])
            await message.answer(f"Успех! Вот ваши NFT, выставленные на GetGems: {nft_links}",
                                 reply_markup=menu())

        except Exception as e:
            await message.answer(f"Ошибка: {e}",
                                 reply_markup=menu())
        
        await state.finish()

    except ValueError:
        await message.answer("Что-то пошло не так! попробуйте ещё раз")
        await message.answer("Введите минимальную ставку NFT",
                             reply_markup=menu())
        await state.set_state("get_nft_auction_bid")

    except InvalidAddressError:
        await message.answer("Вы ввели неправильный адрес NFT, попробуйте ещё раз")
        await message.answer("Введите адрес NFT",
                             reply_markup=menu())
        await state.set_state("get_nft_auction_address")
