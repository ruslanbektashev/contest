import json

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
    telegram_user_not_authorized, get_account_by_tg_id, json_get, student_table_keyboard, staff_table_keyboard

import telebot


tbot = telebot.TeleBot(BOT_TOKEN)

tbot.set_webhook(f'https://{LOCALHOST_DOMAIN}/{BOT_TOKEN}')


@tbot.message_handler(commands=['start'], chat_types=['private'])
def start_handler(message: types.Message):
    telegram_user = get_telegram_user(message.chat.id)
    contest_user = telegram_user.contest_user
    if telegram_user is None:
        start_message_text = message.chat.first_name
        if message.chat.last_name is not None:
            start_message_text += " " + message.chat.last_name
        keyboard = start_keyboard_non_authorized()
    else:
        start_message_text = f'{get_account_by_tg_id(chat_id=message.chat.id)}'
        if contest_user.is_staff:
            keyboard = staff_table_keyboard(contest_user=contest_user)
        else:
            keyboard = student_table_keyboard(table_type='courses', contest_user=contest_user)
        # keyboard = courses_table_keyboard(telegram_user.contest_user)  # start_keyboard_authorized()

        # try:
        #     for assignment in list(Assignment.objects.filter(user=telegram_user.contest_user, problem__contest__course=list(telegram_user.contest_user.credit_set.filter(user=telegram_user.contest_user))[1].course)):
        #         print(assignment.problem)
        #     #print(list(telegram_user.contest_user.assignment_set.all()))
        #     #print(list(Assignment.objects.filter(user=telegram_user.contest_user)))
        #     #print(list(Assignment.objects.filter(user=telegram_user.contest_user))[0].problem.course)
        # except Exception as e:
        #     print(e)

    start_message_text += ", добро пожаловать в систему МГУ Контест!"
    try:
        tbot.send_message(chat_id=message.chat.id, text=start_message_text, reply_to_message_id=message.id,
                          reply_markup=keyboard)
    except Exception as e:
        print(e)


@tbot.message_handler(text=login_btn_text, chat_types=['private'])
def login_handler(message: types.Message):
    if get_telegram_user(chat_id=message.chat.id) is None:
        login_bot_message = tbot.send_message(chat_id=message.chat.id, text="Введите логин и пароль следующим "
                                                                            "образом:\n"
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


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') in ['go', 'back'])
def goback_callback(call: types.CallbackQuery):
    user = get_telegram_user(call.message.chat.id).contest_user
    action_type = json_get(call.data, 'type')
    destination = json_get(call.data, 'to')
    destination_id = int(json_get(call.data, 'id')) if 'id' in json.loads(call.data) else None
    keyboard = None

    if destination == 'course':
        keyboard = student_table_keyboard(table_type='contests', contest_user=user, table_id=destination_id)
    if action_type == 'go':
        if destination == 'contest':
            keyboard = student_table_keyboard(table_type='problems', contest_user=user, table_id=destination_id)
    else:
        if destination == 'courses_list':
            keyboard = student_table_keyboard(table_type='courses', contest_user=user, table_id=destination_id)
    tbot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                   reply_markup=keyboard)


@tbot.my_chat_member_handler(func=lambda message: message.new_chat_member.status == 'kicked')
def fff_handler(message: types.ChatMemberUpdated):
    print(message.new_chat_member.status)


# @tbot.message_handler(content_types=["text"])
# def get_okn(message):
#     tbot.send_message(message.chat.id, "Hello, bot!")


tbot.add_custom_filter(custom_filters.TextMatchFilter())
tbot.add_custom_filter(custom_filters.TextStartsFilter())
