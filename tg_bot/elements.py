from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

APP_URL = r'https://www.youtube.com/'


def get_website_button():
    web_app_button = InlineKeyboardButton(
        text="Перейти к заказу",
        web_app=WebAppInfo(url=APP_URL)
    )
    keyboard = InlineKeyboardMarkup().add(web_app_button)
    return keyboard

