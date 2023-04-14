import json
import os
import threading

import telebot

from copy import deepcopy

from PyPDF2 import PdfReader, PdfWriter
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.utils import timezone
from openpyxl import load_workbook
from telebot import custom_filters, types
from telebot.types import Message

from accounts.models import Account
from contest.common_settings import SCHEDULE_CHANNELS_IDS
from django.conf import settings
from contest_telegram_bot.constants import login_btn_text, logout_btn_text
from contest_telegram_bot.keyboards import (problem_detail_keyboard, staff_start_keyboard, start_keyboard_unauthorized,
                                            student_table_keyboard, submission_creation_keyboard,
                                            submissions_list_keyboard, settings_keyboard, staff_course_menu_keyboard,
                                            staff_course_students_keyboard, staff_course_contests_keyboard,
                                            staff_course_problems_keyboard, staff_problem_menu_keyboard,
                                            staff_course_student_menu_keyboard)
from contest_telegram_bot.models import TelegramUser, TelegramUserSettings
from contest_telegram_bot.utils import get_account_by_tg_id, get_telegram_user, json_get, tg_authorisation_wrapper, \
    is_schedule_file, is_excel_file, create_file_from_bytes, get_course_label, get_contest_user_by_tg_id, \
    notify_all_specific_tg_users
from contests.forms import AttachmentForm, SubmissionFilesAttachmentMixin
from contests.models import Problem, Submission, Course
from schedule.models import Schedule, ScheduleAttachment, current_week_date_from, current_week_date_to

tbot = telebot.TeleBot(settings.BOT_TOKEN)

tbot.set_webhook(f'{settings.LOCALHOST_DOMAIN}/{settings.BOT_TOKEN}')


def welcome_handler(outer_message: types.Message, welcome_text: str = ", добро пожаловать в систему МГУ Контест!"):
    def send_welcome_message(text: str, message: types.Message, keyboard: types.ReplyKeyboardMarkup):
        text += welcome_text
        tbot.send_message(chat_id=message.chat.id, text=text, reply_to_message_id=message.id,
                          reply_markup=keyboard)

    def callback_for_authorized(message: types.Message):
        contest_user = get_telegram_user(message.chat.id).contest_user
        start_message_text = f'{get_account_by_tg_id(chat_id=message.chat.id)}'
        if contest_user.is_staff:
            keyboard, _ = staff_start_keyboard(staff_contest_user=contest_user)
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
        tbot.register_next_step_handler(message=login_bot_message, callback=login_data_handler)

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
        TelegramUserSettings.objects.get_or_create(contest_user=authorized_user)
        welcome_handler(outer_message=message, welcome_text=', вы успешно авторизовались.')
    else:
        login_err_msg = tbot.send_message(chat_id=message.chat.id, text='Введённые логин или пароль неверны. '
                                                                        'Повторите попытку.')
        tbot.register_next_step_handler(message=login_err_msg, callback=login_data_handler)


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


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'get_settings')
def get_settings_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        tbot.edit_message_text(
            text=f'Настройки пользователя {get_account_by_tg_id(chat_id=call.message.chat.id)}.',
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=settings_keyboard(contest_user=get_telegram_user(chat_id=call.message.chat.id).contest_user)
        )

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'sett')
def setting_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        all_settings = TelegramUserSettings.objects.get(
            contest_user=get_contest_user_by_tg_id(chat_id=call.message.chat.id))
        setting_action = json_get(call.data, 'act')
        setting_name = json_get(call.data, 'name')
        if setting_action == 'text':
            tbot.answer_callback_query(callback_query_id=call.id,
                                       text=all_settings._meta.get_field(setting_name).verbose_name,
                                       show_alert=True)
        elif setting_action == 'chg':
            setattr(all_settings, setting_name, not getattr(all_settings, setting_name))
            all_settings.save()
            tbot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=settings_keyboard(
                    contest_user=get_telegram_user(chat_id=call.message.chat.id).contest_user)
            )

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') in ['go', 'back'])
def goback_students_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        keyboard = None
        user = get_telegram_user(chat_id=call.message.chat.id).contest_user
        action_type = json_get(call.data, 'type')
        destination = json_get(call.data, 'to')
        destination_id = int(json_get(call.data, 'id')) if 'id' in json.loads(call.data) else None
        destination_text = None

        if destination == 'course':
            keyboard, destination_text = student_table_keyboard(table_type='contests', contest_user=user,
                                                                table_id=destination_id)
        if action_type == 'go':
            if destination == 'contest':
                keyboard, destination_text = student_table_keyboard(table_type='problems', contest_user=user,
                                                                    table_id=destination_id)
            elif destination == 'problem':
                keyboard, destination_text = problem_detail_keyboard(contest_user=user, problem_id=destination_id)
        else:
            if destination == 'courses':
                keyboard, destination_text = student_table_keyboard(table_type='courses', contest_user=user,
                                                                    table_id=destination_id)
            elif destination == 'contest':
                keyboard, destination_text = student_table_keyboard(table_type='problems', contest_user=user,
                                                                    table_id=destination_id)
            elif destination == 'problem':
                keyboard, destination_text = problem_detail_keyboard(contest_user=user, problem_id=destination_id)
        tbot.clear_step_handler(message=call.message)
        tbot.edit_message_text(text=destination_text, chat_id=call.message.chat.id, message_id=call.message.id,
                               reply_markup=keyboard)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') in ['staff_go', 'staff_back'])
def goback_staff_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        keyboard = None
        user = get_telegram_user(chat_id=call.message.chat.id).contest_user
        action_type = json_get(call.data, 'type')
        destination = json_get(call.data, 'to')
        destination_id = int(json_get(call.data, 'id')) if 'id' in json.loads(call.data) else None
        destination_text = None

        if destination == 'course':
            keyboard, destination_text = staff_course_menu_keyboard(course_id=destination_id)
        elif destination == 'contests':
            keyboard, destination_text = staff_course_contests_keyboard(course_id=destination_id)
        elif destination == 'contest':
            keyboard, destination_text = staff_course_problems_keyboard(contest_id=destination_id)
        elif destination == 'problem':
            keyboard, destination_text = staff_problem_menu_keyboard(problem_id=destination_id)
        elif destination == 'course_students':
            keyboard, destination_text = staff_course_students_keyboard(course_id=destination_id)
        elif destination == 'stud':
            course_id = int(json_get(call.data, 'crs_id'))
            student_id = int(json_get(call.data, 'stu_id'))
            keyboard, destination_text = staff_course_student_menu_keyboard(course_id=course_id, student_id=student_id)

        if action_type == 'staff_go':
            pass
        else:
            if destination == 'courses':
                keyboard, destination_text = staff_start_keyboard(staff_contest_user=user)

        tbot.clear_step_handler(message=call.message)
        tbot.edit_message_text(text=destination_text, parse_mode='HTML', chat_id=call.message.chat.id,
                               message_id=call.message.id,
                               reply_markup=keyboard)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'prob_sett')
def staff_problem_menu_settings_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        problem_id = int(json_get(call.data, 'prob_id'))
        cur_val = int(json_get(call.data, 'cur_val'))
        keyboard, _ = staff_problem_menu_keyboard(problem_id=problem_id,
                                                  show_submissions_number=not cur_val)

        tbot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                       message_id=call.message.id,
                                       reply_markup=keyboard)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


@tbot.callback_query_handler(func=lambda call: json_get(call.data, 'type') == 'stu_sett')
def staff_student_menu_settings_callback(outer_call: types.CallbackQuery):
    def callback_for_authorized(call: types.CallbackQuery):
        course_id = int(json_get(call.data, 'crs_id'))
        student_id = int(json_get(call.data, 'stu_id'))
        cur_val = int(json_get(call.data, 'cur_val'))
        keyboard, _ = staff_course_student_menu_keyboard(course_id=course_id,
                                                         student_id=student_id,
                                                         show_submissions_number=not cur_val)
        tbot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                       message_id=call.message.id,
                                       reply_markup=keyboard)

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
            tbot.register_next_step_handler(message=call.message, callback=submission_file_handler,
                                            text=call.message.text)

    unauth_callback_inline_keyboard(outer_call=outer_call, callback_for_authorized=callback_for_authorized)


def submission_file_handler(message: Message, text: str):
    # print(json.dumps(message.json, indent=2))
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


@tbot.channel_post_handler(content_types=['document'], func=lambda message: message.chat.id in SCHEDULE_CHANNELS_IDS)
def schedule_callback(message: Message):
    if is_schedule_file(filename=message.document.file_name) is not None:
        def create_schedule_files(schedule):
            ScheduleAttachment.objects.filter(schedule=schedule).delete()
            schedule.date_updated = timezone.now()
            schedule.save()
            schedule_file = message.document
            schedule_filename = schedule_file.file_name
            create_file_from_bytes(
                file_bytes=tbot.download_file(file_path=tbot.get_file(schedule_file.file_id).file_path),
                filename=schedule_filename)
            if is_excel_file(message.document.file_name):
                wb = load_workbook(filename=schedule_filename)
                sheets = wb.sheetnames
                wb.close()
                for sheet in sheets:
                    cur_xls = load_workbook(filename=schedule_filename)
                    cur_sheet_filename = f'{sheet}.xlsx'
                    sheets_to_delete = deepcopy(sheets)
                    sheets_to_delete.remove(sheet)
                    for del_sheet in sheets_to_delete:
                        cur_xls.remove(cur_xls[del_sheet])
                    cur_xls.save(cur_sheet_filename)
                    cur_xls.close()
                    with open(cur_sheet_filename, 'rb') as current_course_sch:
                        ScheduleAttachment.objects.update_or_create(schedule=schedule, name=sheet,
                                                                    file=File(current_course_sch))
                    os.remove(cur_sheet_filename)
            else:
                tmp_pdf_file = open(schedule_filename, 'rb')
                pdf_sch_object = PdfReader(tmp_pdf_file)
                if pdf_sch_object.is_encrypted:
                    pdf_sch_object.decrypt('70')

                for page in list(pdf_sch_object.pages):
                    output = PdfWriter()
                    output.add_page(page)
                    current_course_name = get_course_label(pdf_content=page.extract_text())
                    current_course_filename = f'{current_course_name}.pdf'
                    with open(current_course_filename, "wb") as outputStream:
                        output.write(outputStream)

                    with open(current_course_filename, 'rb') as current_course_sch:
                        ScheduleAttachment.objects.update_or_create(schedule=schedule, name=current_course_name,
                                                                    file=File(current_course_sch))
                    os.remove(current_course_filename)
                tmp_pdf_file.close()
            os.remove(schedule_filename)

        current_date = timezone.now()
        if 1 <= current_date.isocalendar()[2] <= 4:
            next_week = False
            week = 'эту неделю'
        else:
            next_week = True
            week = 'следующую неделю'

        try:
            new_schedule = Schedule.objects.get(date_from=current_week_date_from(next_week=next_week),
                                                date_to=current_week_date_to(next_week=next_week))
            schedule_update_time_passed = (timezone.now() - new_schedule.date_updated).seconds
            if schedule_update_time_passed <= 40:
                threading.Timer(40 - schedule_update_time_passed, create_schedule_files, [new_schedule]).start()
            else:
                create_schedule_files(new_schedule)
            action = 'Обновлено'
        except ObjectDoesNotExist:
            # TODO: убрать костыльный owner_id и заменить его на id специального пользователя или None
            new_schedule, _ = Schedule.objects.get_or_create(date_created=current_date, date_updated=current_date,
                                                             date_from=current_week_date_from(next_week=next_week),
                                                             date_to=current_week_date_to(next_week=next_week),
                                                             owner=User.objects.get(username='telegram_bot'))
            create_schedule_files(new_schedule)
            action = 'Добавлено'

        recipients = TelegramUser.objects.filter(contest_user__is_active=True,
                                                 contest_user__is_staff=False,
                                                 contest_user__is_superuser=False)
        notify_all_specific_tg_users(notification_msg=f'{action} <b>расписание на {week} ({new_schedule})</b>',
                                     tg_users=recipients, notification_obj=new_schedule)


@tbot.message_handler(func=lambda message: message.text == '1')
def test_handler(message: types.Message):
    try:
        print(Account.objects.filter(level=4))
    except Exception as e:
        print(e)


@tbot.my_chat_member_handler(func=lambda message: message.new_chat_member.status == 'kicked')
def fff_handler(message: types.ChatMemberUpdated):
    print(message.new_chat_member.status)


# @tbot.message_handler(content_types=["text"])
# def get_okn(message):
#     tbot.send_message(message.chat.id, "Hello, bot!")


tbot.add_custom_filter(custom_filters.TextMatchFilter())
tbot.add_custom_filter(custom_filters.TextStartsFilter())
