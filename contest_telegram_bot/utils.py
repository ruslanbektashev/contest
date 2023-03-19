import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from emoji import emojize
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from accounts.models import Account
from contest_telegram_bot.constants import help_btn_text, login_btn_text, logout_btn_text

from contest_telegram_bot.models import TelegramUser
from contests.models import Assignment, Contest, Course


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
    table_list = list(course for course in Course.objects.filter(leaders__account=Account.objects.get(user=contest_user)))
    for course in table_list:
        keyboard.row(InlineKeyboardButton(text=str(course), callback_data=json.dumps({'type': 'course'})))

    return keyboard


# 1. Login_required decorator for bot; 2. save 3 functions for 3 keyboards; 3. Emojis for course list,
#  for settings, etc.; 4. Bot settings and user settings; 5. Logout keyboard (inline or ordinary?)

def student_table_keyboard(table_type: str, contest_user: User, table_id: int = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_list = None
    table_header = None
    back_btn = None
    if table_type == 'courses':
        table_list = list([credit.course, credit.score] for credit in contest_user.credit_set.all())
        table_header = ['Курс', 'Оценка']
        back_btn = None
    elif table_type == 'contests':
        table_list = list(set(assignment.contest for assignment in
                              contest_user.assignment_set.filter(problem__contest__course_id=table_id)))
        table_list.reverse()
        table_header = ['Раздел']
        back_btn = goback_button(goback_type='back', to='courses_list')
    elif table_type == 'problems':
        table_list = list([problem.problem, problem.score] for problem in
                          contest_user.assignment_set.filter(problem__contest_id=table_id))
        table_list.reverse()
        table_header = ['Задача', 'Оценка']
        contest = Contest.objects.get(pk=table_id)
        back_btn = goback_button(goback_type='back', to='course', to_id=contest.course_id)

    none_type_row(keyboard, table_header)
    if len(table_list) == 0:
        none_type_row(keyboard, ['Заданий нет'])

    if table_type in ['courses', 'problems']:
        for table_obj, score in table_list:
            keyboard.row(
                goback_button(goback_type='go', to='course', to_id=table_obj.id, text=str(table_obj)),
                score_button(score)
            )
    else:
        for contest in table_list:
            keyboard.row(goback_button(goback_type='go', to='contest', to_id=contest.id, text=str(contest)))

    if back_btn is not None:
        keyboard.row(back_btn)
    return keyboard





# def courses_table_keyboard(contest_user: User):
#     courses_keyboard = InlineKeyboardMarkup(row_width=1)
#     courses_list = list([credit.course, credit.score] for credit in contest_user.credit_set.all())
#     none_type_row(courses_keyboard, ['Курс', 'Оценка'])
#     for course, course_score in courses_list:
#         courses_keyboard.row(
#             InlineKeyboardButton(text=str(course),
#                                  callback_data=json.dumps({'type': 'go', 'to': 'course', 'id': course.id})),
#             score_button(course_score)
#         )
#     return courses_keyboard
#
#
# def contests_table_keyboard(contest_user: User, course_id: int):
#     contests_keyboard = InlineKeyboardMarkup(row_width=1)
#     contests_list = list(set(assignment.contest for assignment in
#                              contest_user.assignment_set.filter(problem__contest__course_id=course_id)))
#     none_type_row(contests_keyboard, ['Раздел'])
#     for contest in reversed(contests_list):
#         contests_keyboard.row(InlineKeyboardButton(text=str(contest),
#                                                    callback_data=json.dumps(
#                                                        {'type': 'go', 'to': 'contest', 'id': contest.id})))
#     contests_keyboard.row(back_button('courses_list'))
#     return contests_keyboard
#
#
# def problems_table_keyboard(contest_user: User, contest_id: int):
#     contest = Contest.objects.get(pk=contest_id)
#     problems_keyboard = InlineKeyboardMarkup(row_width=1)
#     problems_list = list([problem.problem, problem.score] for problem in
#                          contest_user.assignment_set.filter(problem__contest_id=contest_id))
#     none_type_row(problems_keyboard, ['Задача', 'Оценка'])
#     for problem, problem_score in reversed(problems_list):
#         problems_keyboard.row(InlineKeyboardButton(text=str(problem),
#                                                    callback_data=json.dumps(
#                                                        {'type': 'go', 'to': 'problem', 'id': problem.id})),
#                               score_button(problem_score))
#     problems_keyboard.row(back_button('course', contest.course_id))
#     return problems_keyboard


def json_get(json_str: str, key: str):
    return json.loads(json_str)[key]
