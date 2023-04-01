import json
import os

import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import telebot
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files import File
from django.utils import timezone
from telebot import custom_filters, types
from telebot.types import Message

from contest.common_settings import SCHEDULE_CHANNELS_IDS
from contest.settings import LOCALHOST_DOMAIN, BOT_TOKEN
from contest_telegram_bot.constants import login_btn_text, logout_btn_text
from contest_telegram_bot.keyboards import (problem_detail_keyboard, staff_table_keyboard, start_keyboard_unauthorized,
                                            student_table_keyboard, submission_creation_keyboard,
                                            submissions_list_keyboard)
from contest_telegram_bot.models import TelegramUser
from contest_telegram_bot.utils import get_account_by_tg_id, get_telegram_user, json_get, tg_authorisation_wrapper, \
    is_schedule_file, is_excel_file
from contests.forms import AttachmentForm, SubmissionFilesAttachmentMixin
from contests.models import Problem, Submission
from schedule.models import Schedule, ScheduleAttachment, current_week_date_from, current_week_date_to

tbot = telebot.TeleBot(settings.BOT_TOKEN)

tbot.set_webhook(f'{LOCALHOST_DOMAIN}/{BOT_TOKEN}')


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
            keyboard, _ = student_table_keyboard(table_type='courses', contest_user=contest_user)
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
        destination_text = None

        if destination == 'course':
            keyboard, destination_text = student_table_keyboard(table_type='contests', contest_user=user, table_id=destination_id)
        if action_type == 'go':
            if destination == 'contest':
                keyboard, destination_text = student_table_keyboard(table_type='problems', contest_user=user, table_id=destination_id)
            elif destination == 'problem':
                keyboard, destination_text = problem_detail_keyboard(contest_user=user, problem_id=destination_id)
        else:
            if destination == 'courses_list':
                keyboard, destination_text = student_table_keyboard(table_type='courses', contest_user=user, table_id=destination_id)
            elif destination == 'contest':
                keyboard, destination_text = student_table_keyboard(table_type='problems', contest_user=user, table_id=destination_id)
            elif destination == 'problem':
                keyboard, destination_text = problem_detail_keyboard(contest_user=user, problem_id=destination_id)
        tbot.clear_step_handler(message=call.message)
        tbot.edit_message_text(text=destination_text, chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)

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


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'submission')
def submission_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        user = get_telegram_user(chat_id=call.message.chat.id).contest_user
        problem_id = json_get(call.data, 'id')
        problem = Problem.objects.get(pk=problem_id)
        action = json_get(call.data, 'action')
        programs_allowed_extensions = list(AttachmentForm().FILES_ALLOWED_EXTENSIONS)
        files_allowed_extensions = SubmissionFilesAttachmentMixin().FILES_ALLOWED_EXTENSIONS
        if action == 'create':
            tbot.edit_message_text(text=f'Отправьте файлы.\nДопустимы следующие форматы: '
                                        f'<code>{", ".join(programs_allowed_extensions)}</code>',
                                   parse_mode='HTML',
                                   chat_id=call.message.chat.id,
                                   message_id=call.message.id,
                                   reply_markup=submission_creation_keyboard(problem_id=problem_id))
            tbot.register_next_step_handler(message=call.message, callback=submission_file_handler, text=call.message.text)
    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


def submission_file_handler(message: Message, text: str):
    #print(json.dumps(message.json, indent=2))
    file_info = tbot.get_file(message.document.file_id)
    print(file_info)
    file = tbot.download_file(file_path=file_info.file_path)
    print(file)
    with open('C:/new_file.cpp', 'wb') as new_file:
        new_file.write(file)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'status')
def status_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        submission_id = int(json_get(call.data, 'status_obj_id'))
        tbot.answer_callback_query(callback_query_id=call.id,
                                   text=f'{Submission.objects.get(pk=submission_id).get_status_display()}',
                                   show_alert=True)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


# class ScheduleHandler:
#     first_schedule_sent = False
#     first_sch_file = None

first_schedule_sent = False
first_sch_file = None


@tbot.channel_post_handler(content_types=['document'], func=lambda message: (message.chat.id in SCHEDULE_CHANNELS_IDS) and not first_schedule_sent)
def schedule_callback(message: Message):
    if is_schedule_file(filename=message.document.file_name) is not None:
        global first_schedule_sent
        global first_sch_file
        first_schedule_sent = True
        first_sch_file = message.document


@tbot.channel_post_handler(content_types=['document'], func=lambda message: (message.chat.id in SCHEDULE_CHANNELS_IDS) and first_schedule_sent)
def schedule_final_callback(message: Message):
    second_sch_file = message.document
    if second_sch_file is not None:
        if is_schedule_file(filename=second_sch_file.file_name):
            current_date = timezone.now()
            # TODO: убрать костыльный owner_id и заменить его на id специального пользователя или None
            new_schedule, _ = Schedule.objects.get_or_create(date_created=current_date, date_updated=current_date,
                                                             date_from=current_week_date_from(next_week=True),
                                                             date_to=current_week_date_to(next_week=True),
                                                             owner_id=1357)
            if is_excel_file(filename=first_sch_file.file_name) is not None:
                excel_sch_file = first_sch_file
                pdf_sch_file = second_sch_file
            else:
                excel_sch_file = second_sch_file
                pdf_sch_file = first_sch_file

            excel_sch_bytes = tbot.download_file(tbot.get_file(excel_sch_file.file_id).file_path)
            pdf_sch_bytes = tbot.download_file(tbot.get_file(pdf_sch_file.file_id).file_path)
            pdf_sch_filename = pdf_sch_file.file_name
            excel_sch_file_sheets = pd.ExcelFile(excel_sch_bytes).sheet_names
            with open(pdf_sch_filename, 'wb') as tmp_pdf_file:
                tmp_pdf_file.write(pdf_sch_bytes)

            tmp_pdf_file = open(pdf_sch_filename, 'rb')
            pdf_sch_object = PdfReader(tmp_pdf_file)
            if pdf_sch_object.is_encrypted:
                pdf_sch_object.decrypt('70')
            for i in range(len(pdf_sch_object.pages)):
                output = PdfWriter()
                output.add_page(pdf_sch_object.pages[i])
                current_course_name = excel_sch_file_sheets[i]
                current_course_filename = f'{current_course_name}.pdf'
                with open(current_course_filename, "wb") as outputStream:
                    output.write(outputStream)

                with open(current_course_filename, 'rb') as current_course_sch:
                    ScheduleAttachment.objects.update_or_create(schedule=new_schedule, name=current_course_name,
                                                                file=File(current_course_sch))
                os.remove(current_course_filename)
            tmp_pdf_file.close()
            os.remove(pdf_sch_filename)
    global first_schedule_sent
    first_schedule_sent = False


@tbot.my_chat_member_handler(func=lambda message: message.new_chat_member.status == 'kicked')
def fff_handler(message: types.ChatMemberUpdated):
    print(message.new_chat_member.status)


# @tbot.message_handler(content_types=["text"])
# def get_okn(message):
#     tbot.send_message(message.chat.id, "Hello, bot!")


tbot.add_custom_filter(custom_filters.TextMatchFilter())
tbot.add_custom_filter(custom_filters.TextStartsFilter())
