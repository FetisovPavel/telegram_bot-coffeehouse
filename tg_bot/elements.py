from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

APP_URL = r'https://www.youtube.com/'


def get_website_button():
    web_app_button = InlineKeyboardButton(
        text="Перейти к заказу",
        web_app=WebAppInfo(url=APP_URL)
    )
    keyboard = InlineKeyboardMarkup().add(web_app_button)
    return keyboard


def get_loyalty_confirm_button():
    button = InlineKeyboardButton(
        text="Подтвердить",
        callback_data='loyalty_confirm_button'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard


def get_pay_balance_button():
    button = InlineKeyboardButton(
        text="Пополнить баланс",
        callback_data='pay_balance_button'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard
