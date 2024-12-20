import logging
import os

import aiogram
from aiogram import Dispatcher, types
from aiogram.types import ContentType
from database.database import get_user, post_user, update_user, get_user_state, get_order, post_item_in_order, \
    get_unfinished_order, get_order_items, get_menu_item, update_order, get_payment_order, get_orders
from tg_bot import elements
from tg_bot.create_bot import bot
from tg_bot.logger.logger import print_error_double_click


async def process_start(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        user = get_user(user_id)
        if not user:
            post_user(user_id)

        await bot.send_message(
            chat_id=user_id,
            text="Выберите кофе для заказа:",
            reply_markup=elements.get_coffee_position_button()
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_position(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    coffee_id = callback_query.data.split('_')[1]

    try:
        await bot.edit_message_text(
            text=f"Выберите объем для {elements.coffee_positions[int(coffee_id) - 1]['name']}:",
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=elements.get_create_size_buttons(coffee_id)
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_size(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    coffee_id, size = callback_query.data.split('_')[1:3]

    try:
        await bot.edit_message_text(
            text=f"Выберите количество для {elements.coffee_positions[int(coffee_id) - 1]['name']} ({size} мл):",
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=elements.get_create_quantity_buttons(coffee_id, size)
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_quantity(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    coffee_id, size, quantity = callback_query.data.split('_')[1:]

    try:

        post_item_in_order(user_id, coffee_id, quantity, size)

        await bot.edit_message_text(
            text="Выберите кофе для заказа:",
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=elements.get_coffee_position_button()
        )

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_finish_order(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        order = get_unfinished_order(user_id)

        if order:
            order_items = get_order_items(order.id)

            order_details = f"Ваш заказ:\n\n"
            total_price = 0

            for item in order_items:
                menu_item = get_menu_item(item.menu_item_id)
                item_total = menu_item.price * item.quantity
                total_price += item_total
                order_details += f"{menu_item.name} - {item.quantity} шт. по {menu_item.price} руб. = {item_total} руб.\n"

            update_order(order.id, {'total_price': total_price})

            order_details += f"\nОбщая сумма: {total_price} руб."

            await callback_query.message.answer(order_details, reply_markup=elements.get_order_confirm_button())

        else:
            await callback_query.message.answer("У вас нет незавершённых заказов.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_order_confirm(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        order = get_unfinished_order(user_id)

        if order:
            order_items = get_order_items(order.id)

            order_details = f"Ваш заказ:\n\n"
            total_price = 0

            for item in order_items:
                menu_item = get_menu_item(item.menu_item_id)
                item_total = menu_item.price * item.quantity
                total_price += item_total
                order_details += f"{menu_item.name} - {item.quantity} шт. по {menu_item.price} руб. = {item_total} руб.\n"

            order_details += f"\nОбщая сумма: {total_price} руб."

            update_order(order.id, {'status': 'during_payment'})

            amount = total_price * 100

            await bot.send_invoice(
                chat_id=user_id,
                title=f"Оплата заказа №{order.id}",
                description=order_details,
                payload="pay_order",
                provider_token=os.getenv('YOOTOKEN'),
                currency="RUB",
                start_parameter="pay_order",
                prices=[{"label": "Руб", "amount": amount}]
            )

        else:
            await callback_query.message.answer("У вас нет незавершённых заказов.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_getting_orders(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        orders = get_orders(user_id)

        if not orders:
            await message.answer("У вас нет оплаченных заказов.")
        else:
            order_details = "Ваши оплаченные заказы:\n\n"
            for order in orders:
                order_details += f"Заказ #{order.id} - Статус: {order.status}\n"

            await message.answer(order_details)

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


async def process_successful_pay(message: types.Message):
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

        elif message.successful_payment.invoice_payload == 'pay_order':
            sum_balance = message.successful_payment.total_amount // 100
            order = get_payment_order(user_id)
            update_order(order.id, {'status': "In processing"})
            await bot.send_message(user_id, f"Вы успешно оплатили заказ №{order.id} на сумму "
                                            f"{sum_balance} рублей!\n\n"
                                            f"Текущий статус заказа: В обработке")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start, commands=['start'])
    dp.register_message_handler(process_wallet, commands=['wallet'])
    dp.register_message_handler(process_getting_orders, commands=['order_status'])
    dp.register_callback_query_handler(process_position, lambda c: c.data.startswith("position_"))
    dp.register_callback_query_handler(process_size, lambda c: c.data.startswith("size_"))
    dp.register_callback_query_handler(process_quantity, lambda c: c.data.startswith("quantity_"))
    dp.register_callback_query_handler(process_finish_order, lambda c: c.data.startswith("order_confirmation_"))
    dp.register_callback_query_handler(process_order_confirm, lambda c: c.data.startswith("order_confirm_"))
    dp.register_callback_query_handler(process_create_wallet, lambda c: c.data.startswith('loyalty_confirm_'))
    dp.register_callback_query_handler(process_choose_money, lambda c: c.data.startswith('pay_balance_'))
    dp.register_message_handler(process_check_money_for_pay_balance,
                                lambda message: get_user_state(message.from_user.id) == 'choose_money')
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(process_successful_pay, content_types=ContentType.SUCCESSFUL_PAYMENT)
