from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from telebot import types, custom_filters
from telebot.custom_filters import TextFilter
from telebot.types import Message

from accounts.models import Account
from contest.settings import BOT_TOKEN, LOCALHOST_DOMAIN
# from telebot.custom_filters import Filter
from contest_telegram_bot.constants import login_btn_text, logout_btn_text
from contest_telegram_bot.models import TelegramUser
from contest_telegram_bot.utils import get_telegram_user, start_keyboard_authorized, start_keyboard_non_authorized, \
    telegram_user_not_authorized, get_account_by_tg_id

import telebot

tbot = telebot.TeleBot(BOT_TOKEN)


tbot.set_webhook(f'https://{LOCALHOST_DOMAIN}/{BOT_TOKEN}')


@tbot.message_handler(commands=['start'], chat_types=['private'])
def start_handler(message: types.Message):
    if get_telegram_user(message.chat.id) is None:
        start_message_text = message.chat.first_name
        if message.chat.last_name is not None:
            start_message_text += " " + message.chat.last_name
        keyboard = start_keyboard_non_authorized()
    else:
        start_message_text = f'{get_account_by_tg_id(chat_id=message.chat.id)}'
        keyboard = start_keyboard_authorized()

    start_message_text += ", добро пожаловать в систему МГУ Контест!"
    tbot.send_message(chat_id=message.chat.id, text=start_message_text, reply_to_message_id=message.id,
                      reply_markup=keyboard)


@tbot.message_handler(text=login_btn_text, chat_types=['private'])
def login_handler(message: types.Message):
    if get_telegram_user(chat_id=message.chat.id) is None:
        login_bot_message = tbot.send_message(chat_id=message.chat.id, text="Введите логин и пароль следующим "
                                                                            "образом:\n "
                                                                            "<логин>\n<пароль>", reply_markup=None)
        tbot.register_next_step_handler(login_bot_message, login_data_handler)
    else:
        tbot.send_message(chat_id=message.chat.id, text=f'Вы уже вошли в систему как '
                                                        f'{get_account_by_tg_id(chat_id=message.chat.id)}.',
                          reply_markup=start_keyboard_authorized())


def login_data_handler(message: types.Message):
    login_data = message.text.split()
    username = login_data[0]
    if len(login_data) >= 2:
        password = login_data[1]
        authorized_user = authenticate(username=username, password=password)
    else:
        authorized_user = None
    if authorized_user is not None:
        TelegramUser.objects.get_or_create(chat_id=message.chat.id, contest_user=authorized_user)
        tbot.send_message(chat_id=message.chat.id, text=f'Вы успешно авторизовались как '
                                                        f'{get_account_by_tg_id(chat_id=message.chat.id)}.',
                          reply_markup=start_keyboard_authorized())
    else:
        login_err_msg = tbot.send_message(chat_id=message.chat.id, text='Введённые логин или пароль неверны. '
                                                                        'Повторите попытку.')
        tbot.register_next_step_handler(login_err_msg, login_data_handler)


@tbot.message_handler(text=logout_btn_text, chat_types=['private'])
def logout_handler(message: types.Message):
    if get_telegram_user(chat_id=message.chat.id) is not None:
        keyboard = start_keyboard_non_authorized()
        tbot.send_message(chat_id=message.chat.id, text=f"Вы успешно вышли из аккаунта "
                                                        f"{get_account_by_tg_id(chat_id=message.chat.id)}",
                          reply_markup=keyboard)
        TelegramUser.objects.get(chat_id=message.chat.id).delete()


@tbot.my_chat_member_handler(func=lambda message: message.new_chat_member.status == 'kicked')
def fff_handler(message: types.ChatMemberUpdated):
    print(message.new_chat_member.status)


# @tbot.message_handler(content_types=["text"])
# def get_okn(message):
#     tbot.send_message(message.chat.id, "Hello, bot!")


tbot.add_custom_filter(custom_filters.TextMatchFilter())
