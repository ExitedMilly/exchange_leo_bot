from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Актуальный курс')],
            [KeyboardButton(text='Часто задаваемые вопросы')],
            [KeyboardButton(text='Поменять валюту')],
            [KeyboardButton(text='Связь с менеджером')]
        ],
        resize_keyboard=True
    )


def confirm_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Да')],
            [KeyboardButton(text='Нет')]
        ],
        resize_keyboard=True
    )
