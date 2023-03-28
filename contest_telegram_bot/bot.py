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
from contest_telegram_bot.utils import get_telegram_user, get_account_by_tg_id, json_get, tg_authorisation_wrapper
from contest_telegram_bot.keyboards import start_keyboard_unauthorized, student_table_keyboard, \
    staff_table_keyboard, problem_detail_keyboard, submissions_list_keyboard

import telebot

from contests.models import Problem, Submission

tbot = telebot.TeleBot(BOT_TOKEN)


def welcome_handler(outer_message: types.Message, welcome_text: str = ", добро пожаловать в систему МГУ Контест!"):
    def send_welcome_message(text: str, message: types.Message, keyboard: types.ReplyKeyboardMarkup):
        text += welcome_text
        tbot.send_message(chat_id=message.chat.id, text=text, reply_to_message_id=message.id,
                          reply_markup=keyboard)

    def callback_for_authorized(message: types.Message):
        contest_user = get_telegram_user(message.chat.id).contest_user
        start_message_text = f'{get_account_by_tg_id(chat_id=message.chat.id)}'
        if contest_user.is_staff:
            keyboard = staff_table_keyboard(contest_user=contest_user)
        else:
            keyboard = student_table_keyboard(table_type='courses', contest_user=contest_user)
        send_welcome_message(text=start_message_text, message=message, keyboard=keyboard)

    def callback_for_unauthorized(message: types.Message):
        start_message_text = message.chat.first_name
        if message.chat.last_name is not None:
            start_message_text += " " + message.chat.last_name
        keyboard = start_keyboard_unauthorized()
        send_welcome_message(text=start_message_text, message=message, keyboard=keyboard)

    all_callbacks_kwargs = {'message': outer_message}
    tg_authorisation_wrapper(chat_id=outer_message.chat.id, authorized_fun=callback_for_authorized,
                             unauthorized_fun=callback_for_unauthorized, auth_fun_args=all_callbacks_kwargs,
                             unauth_fun_args=all_callbacks_kwargs)


@tbot.message_handler(commands=['start'], chat_types=['private'])
def start_handler(outer_message: types.Message):
    welcome_handler(outer_message=outer_message)


@tbot.message_handler(text=login_btn_text, chat_types=['private'])
def login_handler(outer_message: types.Message):
    def callback_for_authorized(message: types.Message):
        tbot.send_message(chat_id=message.chat.id, text=f'Вы уже вошли в систему как '
                                                        f'{get_account_by_tg_id(chat_id=message.chat.id)}.')

    def callback_for_unauthorized(message: types.Message):
        login_bot_message = tbot.send_message(chat_id=message.chat.id, text="Введите логин и пароль следующим "
                                                                            "образом:\n"
                                                                            "<логин>\n<пароль>", reply_markup=None)
        tbot.register_next_step_handler(login_bot_message, login_data_handler)

    all_callbacks_kwargs = {'message': outer_message}
    tg_authorisation_wrapper(chat_id=outer_message.chat.id, authorized_fun=callback_for_authorized,
                             unauthorized_fun=callback_for_unauthorized, auth_fun_args=all_callbacks_kwargs,
                             unauth_fun_args=all_callbacks_kwargs)


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
        welcome_handler(outer_message=message, welcome_text=', вы успешно авторизовались.')

    else:
        login_err_msg = tbot.send_message(chat_id=message.chat.id, text='Введённые логин или пароль неверны. '
                                                                        'Повторите попытку.')
        tbot.register_next_step_handler(login_err_msg, login_data_handler)


def unauth_callback_inline_keyboard(outer_call: types.CallbackQuery, callback_for_authorized):
    def callback_for_unauthorized(call: types.CallbackQuery):
        tbot.edit_message_text(text='Вы не вошли ни в один аккаунт.', chat_id=call.message.chat.id,
                               message_id=call.message.id,
                               reply_markup=None)

    all_callbacks_kwargs = {'call': outer_call}
    tg_authorisation_wrapper(chat_id=outer_call.message.chat.id, authorized_fun=callback_for_authorized,
                             unauthorized_fun=callback_for_unauthorized, auth_fun_args=all_callbacks_kwargs,
                             unauth_fun_args=all_callbacks_kwargs)


@tbot.message_handler(text=logout_btn_text, chat_types=['private'])
def logout_handler(message: types.Message):
    if get_telegram_user(chat_id=message.chat.id) is not None:
        keyboard = start_keyboard_unauthorized()
        tbot.send_message(chat_id=message.chat.id, text=f"Вы успешно вышли из аккаунта "
                                                        f"{get_account_by_tg_id(chat_id=message.chat.id)}.",
                          reply_markup=keyboard)
        TelegramUser.objects.get(chat_id=message.chat.id).delete()


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'exit')
def logout_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        tbot.edit_message_text(
            text=f'Вы успешно вышли из аккаунта {get_account_by_tg_id(chat_id=call.message.chat.id)}.',
            chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=None
        )
        TelegramUser.objects.get(chat_id=call.message.chat.id).delete()

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') in ['go', 'back'])
def goback_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        keyboard = None
        user = get_telegram_user(chat_id=call.message.chat.id).contest_user
        action_type = json_get(call.data, 'type')
        destination = json_get(call.data, 'to')
        destination_id = int(json_get(call.data, 'id')) if 'id' in json.loads(call.data) else None

        if destination == 'course':
            keyboard = student_table_keyboard(table_type='contests', contest_user=user, table_id=destination_id)
        if action_type == 'go':
            if destination == 'contest':
                keyboard = student_table_keyboard(table_type='problems', contest_user=user, table_id=destination_id)
            elif destination == 'problem':
                keyboard = problem_detail_keyboard(contest_user=user, problem_id=destination_id)
        else:
            if destination == 'courses_list':
                keyboard = student_table_keyboard(table_type='courses', contest_user=user, table_id=destination_id)
            elif destination == 'contest':
                keyboard = student_table_keyboard(table_type='problems', contest_user=user, table_id=destination_id)
            elif destination == 'problem':
                keyboard = problem_detail_keyboard(contest_user=user, problem_id=destination_id)
        tbot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'problem')
def problem_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        user = get_telegram_user(chat_id=call.message.chat.id).contest_user
        problem_id = json_get(call.data, 'id')
        problem_item = json_get(call.data, 'item')
        problem = Problem.objects.get(pk=problem_id)
        if problem_item == 'description':
            tbot.answer_callback_query(callback_query_id=call.id,
                                       text=f'{problem.description}', show_alert=True)
        elif problem_item == 'submissions':
            tbot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id,
                                           reply_markup=submissions_list_keyboard(contest_user=user,
                                                                                  problem_id=problem_id))

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'status')
def status_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        submission_id = int(json_get(call.data, 'status_obj_id'))
        tbot.answer_callback_query(callback_query_id=call.id,
                                   text=f'{Submission.objects.get(pk=submission_id).get_status_display()}',
                                   show_alert=True)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.my_chat_member_handler(func=lambda message: message.new_chat_member.status == 'kicked')
def fff_handler(message: types.ChatMemberUpdated):
    print(message.new_chat_member.status)


# @tbot.message_handler(content_types=["text"])
# def get_okn(message):
#     tbot.send_message(message.chat.id, "Hello, bot!")


tbot.add_custom_filter(custom_filters.TextMatchFilter())
tbot.add_custom_filter(custom_filters.TextStartsFilter())
