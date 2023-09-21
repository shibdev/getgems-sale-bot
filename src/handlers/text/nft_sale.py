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
from contracts import SaleContract
from itertools import zip_longest


async def enter_nft_sale_price(message: types.Message, state: FSMContext):
    await state.update_data(nft_address=message.text.split("\n"))
    await message.answer("Введите цену продажи NFT",
                         reply_markup=menu())
    await state.set_state("get_nft_sale_price")

async def send_nft_sale_transaction(message: types.Message, state: FSMContext):
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

        amount = message.text.split("\n")
    
        data = await state.get_data()
        user_address = Address(get_user_address(message.from_user.id))

        for nft_address, nft_amount in zip_longest(data["nft_address"], amount, fillvalue=amount[-1]):
            fees_cell = begin_cell()\
                        .store_address(user_address)\
                        .store_coins(0)\
                        .store_address(user_address)\
                        .store_coins(0)\
                        .end_cell()\
            
            sale_data_cell = begin_cell()\
                            .store_bit(0)\
                            .store_uint(int(time.time()), 32)\
                            .store_address(user_address)\
                            .store_address(Address(nft_address))\
                            .store_address(user_address)\
                            .store_coins(int(float(nft_amount)*1e9))\
                            .store_ref(fees_cell)\
                            .store_bit(0)\
                            .end_cell()\
            
            sale_contract = SaleContract(
                data_cell=sale_data_cell
            )

            sale_body = begin_cell()\
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
                                    .store_ref(sale_contract.create_state_init()["state_init"])\
                                    .store_ref(sale_body)\
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
        await message.answer("Вы ввели неправильное число, попробуйте ещё раз")
        await message.answer("Введите цену продажи NFT",
                             reply_markup=menu())
        await state.set_state("get_nft_sale_price")

    except InvalidAddressError:
        await message.answer("Вы ввели неправильный адрес NFT, попробуйте ещё раз")
        await message.answer("Введите адрес NFT",
                             reply_markup=menu())
        await state.set_state("get_nft_sale_address")
