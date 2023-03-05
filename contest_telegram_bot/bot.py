from telebot import types
from contest.settings import BOT_TOKEN

import telebot

tbot = telebot.TeleBot(BOT_TOKEN)


@tbot.message_handler(commands=['start'])
def start_handler(message: types.Message):
    start_message_text = message.chat.first_name
    if message.chat.last_name is not None:
        start_message_text += " " + message.chat.last_name
    start_message_text += ", добро пожаловать в систему МГУ Контест! Пожалуйста, введите"
    tbot.send_message(message.chat.id, start_message_text)


# @tbot.message_handler(content_types=["text"])
# def get_okn(message):
#     tbot.send_message(message.chat.id, "Hello, bot!")

