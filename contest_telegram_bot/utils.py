import json
import locale

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from emoji import emojize
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from accounts.models import Account
from contest_telegram_bot.constants import help_btn_text, login_btn_text, logout_btn_text, courses_emoji, contest_emoji, \
    bot_settings_emoji, user_settings_emoji, problem_emoji

from contest_telegram_bot.models import TelegramUser
from contests.models import Assignment, Contest, Course, Problem


def get_telegram_user(chat_id: int):
    try:
        return TelegramUser.objects.get(chat_id=chat_id)
    except ObjectDoesNotExist:
        return None


def get_account_by_tg_id(chat_id: int):
    try:
        tg_user = TelegramUser.objects.get(chat_id=chat_id)
        return Account.objects.get(user=tg_user.contest_user)
    except ObjectDoesNotExist:
        return None


def telegram_user_not_authorized(chat_id: int):
    tg_user = get_telegram_user(chat_id)
    if tg_user is not None:
        if tg_user.contest_user is None:
            return True
    return False


def start_keyboard_authorized():
    login_btn = KeyboardButton(logout_btn_text)
    help_btn = KeyboardButton(help_btn_text)
    test_btn = KeyboardButton('TEST')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.row(login_btn, help_btn)
    # keyboard.add(*[login_btn, help_btn])
    # keyboard.add(*[login_btn, help_btn])
    return keyboard


def start_keyboard_non_authorized():
    login_btn = KeyboardButton(login_btn_text)
    help_btn = KeyboardButton(help_btn_text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(login_btn, help_btn)
    return keyboard


def none_type_row(keyboard: InlineKeyboardMarkup, titles: list):
    buttons = []
    for title in titles:
        buttons.append(InlineKeyboardButton(text=title, callback_data=json.dumps({'type': 'none'})))
    keyboard.row(*buttons)


def none_type_button(btn_text: str):
    return InlineKeyboardButton(text=btn_text, callback_data=json.dumps({'type': 'none'}))


def score_button(score: int, btn_type: str = 'inline'):
    if btn_type == 'inline':
        return InlineKeyboardButton(text=emojize(f':keycap_{str(score)}:') if score > 0 else '-',
                                    callback_data=json.dumps({'type': 'none'}))
    else:
        return KeyboardButton(text=emojize(f':keycap_{str(score)}:') if score > 0 else '-')


def goback_button(goback_type: str, to: str, to_id: int = None, text: str = None):
    callback_data = {'type': goback_type, 'to': to}
    if to_id is not None:
        callback_data['id'] = to_id
    if text is None:
        btn_text = emojize(':left_arrow:')
    else:
        btn_text = text
    return InlineKeyboardButton(btn_text,
                                callback_data=json.dumps(callback_data))


def staff_table_keyboard(contest_user: User, table_id: int = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_header = ['Ваши курсы']
    none_type_row(keyboard, table_header)
    table_list = list(
        course for course in Course.objects.filter(leaders__account=Account.objects.get(user=contest_user)))
    for course in table_list:
        keyboard.row(InlineKeyboardButton(text=str(course), callback_data=json.dumps({'type': 'course'})))

    return keyboard


# TODO:
#  2. Problems interface: description, submissions list, send submission
#  3. Non_auth -> unauth VEZDE!!
#  4. Bot settings and user settings;
#  5. Logout keyboard (inline or ordinary?)

def student_table_keyboard(table_type: str, contest_user: User, table_id: int = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_list = None
    table_title = None
    table_header = None
    back_btn = None
    if table_type == 'courses':
        table_list = list([credit.course, credit.score] for credit in contest_user.credit_set.all())
        table_title = [f'{courses_emoji} Ваши курсы']
        table_header = ['Курс', 'Оценка']
        back_btn = None
    elif table_type == 'contests':
        table_list = list(set(assignment.contest for assignment in
                              contest_user.assignment_set.filter(problem__contest__course_id=table_id)))
        table_list.reverse()
        table_title = [f'{contest_emoji} {Course.objects.get(pk=table_id)}']
        table_header = ['Разделы']
        back_btn = goback_button(goback_type='back', to='courses_list')
    elif table_type == 'problems':
        table_list = list([problem.problem, problem.score] for problem in
                          contest_user.assignment_set.filter(problem__contest_id=table_id))
        table_list.reverse()
        table_title = [f'{contest_emoji} {Contest.objects.get(pk=table_id)}']
        table_header = ['Задача', 'Оценка']
        contest = Contest.objects.get(pk=table_id)
        back_btn = goback_button(goback_type='back', to='course', to_id=contest.course_id)

    none_type_row(keyboard, table_title)
    none_type_row(keyboard, table_header)
    if len(table_list) == 0:
        none_type_row(keyboard, ['Заданий нет'])

    if table_type in ['courses', 'problems']:
        for table_obj, score in table_list:
            keyboard.row(
                goback_button(goback_type='go', to=table_type[0:-1], to_id=table_obj.id, text=str(table_obj)),
                score_button(score)
            )
    else:
        for contest in table_list:
            keyboard.row(goback_button(goback_type='go', to='contest', to_id=contest.id, text=str(contest)))

    if table_type == 'courses':
        keyboard.row(InlineKeyboardButton(text=f'{user_settings_emoji} Настройки пользователя',
                                          callback_data=json.dumps({'type': 'setting'})))
        keyboard.row(InlineKeyboardButton(text=f'{bot_settings_emoji} Настройки бота',
                                          callback_data=json.dumps({'type': 'setting'})))
        keyboard.row(InlineKeyboardButton(text=logout_btn_text,
                                          callback_data=json.dumps({'type': 'exit'})))

    if back_btn is not None:
        keyboard.row(back_btn)
    return keyboard


def problem_detail_keyboard(contest_user: User, problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    header = [f'{problem_emoji} {problem.title}']
    description_btn = InlineKeyboardButton(text='Описание задачи', callback_data=json.dumps({'type': 'problem',
                                                                                             'item': 'description',
                                                                                             'id': problem_id}))
    submissions_btn = InlineKeyboardButton(text='Посылки к задаче', callback_data=json.dumps({'type': 'problem',
                                                                                              'item': 'submissions',
                                                                                              'id': problem_id}))
    discussion_btn = InlineKeyboardButton(text='Обсуждение задачи', callback_data=json.dumps({'type': 'problem',
                                                                                              'item': 'discussion',
                                                                                              'id': problem_id}))
    back_btn = goback_button(goback_type='back', to='contest', to_id=problem.contest_id)

    none_type_row(keyboard, header)
    keyboard.add(description_btn, submissions_btn, discussion_btn, back_btn)
    return keyboard


def submissions_list_keyboard(contest_user: User, problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    submissions_list = list(problem.submission_set.filter(assignment__user=contest_user))
    title = [f'{problem_emoji} {problem.title}. Посылки']
    header = ['Посылка', 'Статус']
    none_type_row(keyboard, title)
    none_type_row(keyboard, header)
    locale.setlocale(locale.LC_TIME, "Russian")
    for submission in submissions_list:
        keyboard.row(InlineKeyboardButton(text=submission.date_created.strftime('%d %b %Y г. в %H:%M').lower(),
                                          callback_data=json.dumps({'type': 'go', 'to': 'submission'})),
                     InlineKeyboardButton(text=submission.status, callback_data=json.dumps({'type': 'status',
                                                                                            'status_obj_id': submission.id})))

    keyboard.row(goback_button(goback_type='back', to='problem', to_id=problem_id))
    return keyboard


def cyrillic_encode(cyrillic: str):
    return list(cyrillic.encode('utf-8'))


def cyrillic_decode(cyrillic_codes: list):
    return bytes(cyrillic_codes).decode('utf-8')


def tg_authorisation_wrapper(
        chat_id: int,
        authorized_fun,
        unauthorized_fun,
        auth_fun_args: dict,
        unauth_fun_args: dict
):
    if get_telegram_user(chat_id=chat_id) is None:
        unauthorized_fun(**auth_fun_args)
    else:
        authorized_fun(**unauth_fun_args)


def json_get(json_str: str, key: str):
    return json.loads(json_str)[key]
