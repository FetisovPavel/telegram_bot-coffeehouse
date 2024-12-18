import logging
import os

import aiogram
from aiogram import Dispatcher, types
from aiogram.types import ContentType

from database.database import get_user, post_user, update_user, get_user_state
from tg_bot import elements
from tg_bot.create_bot import bot
from tg_bot.logger.logger import print_error_double_click

APP_URL = r'https://www.youtube.com/'


async def process_start(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        user = get_user(user_id)

        if not user:
            post_user(user_id)

        await bot.send_message(
            chat_id=user_id,
            text="Добро пожаловать в кафе 'Coffee House'! ☕\n\n"
                 "Самое время заказать что-нибудь вкусненькое 😋 "
                 "Нажмите на кнопку ниже, чтобы приступить к заказу.",
            reply_markup=elements.get_website_button()
        )

    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_wallet(message: types.Message):
    user_id = str(message.from_user.id)
    try:
        user = get_user(user_id)
        if user.loyalty_points is None:
            await bot.send_message(
                chat_id=user_id,
                text="У вас не создан кошелек!\n\n"
                     "Если хотите вступить в ряды кофеманов нажмите 'Создать' ☕",
                reply_markup=elements.get_loyalty_confirm_button()
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text="Добро пожаловать в кошелек Coffee House! ☕\n\n"
                     "С помощью кошелька вы можете пополнить баланс и использовать его для оплаты заказов "
                     "в нашем кафе. "
                     "При оплате с использованием кошелька вы получите скидку 5% на общую сумму заказа. 🎉\n\n"
                     "Пополните баланс прямо сейчас и наслаждайтесь выгодными покупками!",
                reply_markup=elements.get_pay_balance_button()
            )
            await bot.send_message(
                chat_id=user_id,
                text=f"Ваш текущий баланс: {user.loyalty_points} рублей 😄",
            )

    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_create_wallet(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)

    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        update_user(user_id, {'loyalty_points': 0})
        user = get_user(user_id)

        await bot.send_message(
            chat_id=user_id,
            text="Добро пожаловать в кошелек Coffee House! ☕\n\n"
                 "С помощью кошелька вы можете пополнить баланс и использовать его для оплаты заказов в нашем кафе. "
                 "При оплате с использованием кошелька вы получите скидку 5% на общую сумму заказа. 🎉\n\n"
                 "Пополните баланс прямо сейчас и наслаждайтесь выгодными покупками!",
            reply_markup=elements.get_pay_balance_button()
        )
    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_choose_money(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)

    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        update_user(user_id, {'state': 'choose_money'})

        await bot.send_message(
            chat_id=user_id,
            text="Введите сумму пополнения кошелька.",
        )
    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_check_money_for_pay_balance(message: types.Message):
    user_id = str(message.from_user.id)

    try:

        if message.text.isdigit():
            amount = int(message.text) * 100
            await bot.send_invoice(
                chat_id=user_id,
                title="Пополнение баланса",
                description=f"Пополнение баланса на сумму {message.text}",
                payload="pay_balance",
                provider_token=os.getenv('YOOTOKEN'),
                currency="RUB",
                start_parameter="pay_balance",
                prices=[{"label": "Руб", "amount": amount}]
            )

            update_user(user_id, {'state': 'pay_money'})

        else:
            await bot.send_message(
                chat_id=user_id,
                text="Пожалуйста, введите корректное число для пополнения баланса.",
            )
    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_successful_balance_accrual(message: types.Message):
    user_id = str(message.from_user.id)

    try:

        if message.successful_payment.invoice_payload == 'pay_balance':
            sum_balance = message.successful_payment.total_amount // 100
            user = get_user(user_id)
            final_balance = user.loyalty_points + sum_balance
            update_user(user_id, {'state': 'Default', 'loyalty_points': final_balance})
            await bot.send_message(user_id, f"Вы успешно пополнили баланс на сумму "
                                            f"{sum_balance} рублей!\n\n"
                                            f"Воспользуйтесь командой /wallet, чтобы посмотреть Ваш текущий баланс!")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")




def register_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start, commands=['start'])
    dp.register_message_handler(process_wallet, commands=['wallet'])
    dp.register_callback_query_handler(process_create_wallet, lambda c: c.data.startswith('loyalty_confirm_'))
    dp.register_callback_query_handler(process_choose_money, lambda c: c.data.startswith('pay_balance_'))
    dp.register_message_handler(process_check_money_for_pay_balance,
                                lambda message: get_user_state(message.from_user.id) == 'choose_money')
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(process_successful_balance_accrual, content_types=ContentType.SUCCESSFUL_PAYMENT)
