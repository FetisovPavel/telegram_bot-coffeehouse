import logging

from aiogram import Dispatcher, types

from database.database import get_user, post_user
from tg_bot import elements
from tg_bot.create_bot import bot

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


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start, commands=['start'])
