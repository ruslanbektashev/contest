import json

from django.contrib.auth.models import User
from emoji import emojize
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from accounts.models import Account, Comment
from contest.common_settings import CONTEST_DOMAIN
from contest_telegram_bot.constants import courses_emoji, contest_emoji, user_settings_emoji, \
    logout_btn_text, problem_emoji, submission_status_emojis, login_btn_text, help_btn_text, send_emoji, comments_emoji, \
    marks_emojis, problems_emoji, users_emoji, down_arrow_emoji, selection_emoji, checked_emoji, unchecked_emoji, \
    cross_emoji, hourglass_emoji, back_emoji, plus_emoji
from contest_telegram_bot.models import TelegramUserSettings
from contest_telegram_bot.utils import get_user_assignments, date_to_str, back_to_submissions_text
from contests.models import Course, Contest, Problem, Assignment, Submission, Credit
from schedule.models import Schedule
from support.models import Question, Report


def start_keyboard_authorized():
    login_btn = KeyboardButton(logout_btn_text)
    help_btn = KeyboardButton(help_btn_text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.row(login_btn, help_btn)
    return keyboard


def start_keyboard_unauthorized():
    login_btn = KeyboardButton(login_btn_text)
    help_btn = KeyboardButton(help_btn_text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(login_btn, help_btn)
    return keyboard


def none_type_row(keyboard: InlineKeyboardMarkup, titles: list):
    buttons = []
    for title in titles:
        if isinstance(title, InlineKeyboardButton):
            buttons.append(title)
            continue
        buttons.append(InlineKeyboardButton(text=title, callback_data=json.dumps({'type': 'none'})))
    keyboard.row(*buttons)


def none_type_button(btn_text: str):
    return InlineKeyboardButton(text=btn_text, callback_data=json.dumps({'type': 'none'}))


def score_button(score: int, btn_type: str = 'inline', btn_url=None):
    if btn_type == 'inline':
        return InlineKeyboardButton(text=emojize(f':keycap_{str(score)}:') if score > 0 else '-',
                                    url=btn_url,
                                    callback_data=json.dumps({'type': 'none'}))
    else:
        return KeyboardButton(text=emojize(f':keycap_{str(score)}:') if score > 0 else '-')


def goback_button(goback_type: str, to: str, to_id: int = None, text: str = None):
    callback_data = {'type': goback_type, 'to': to}
    if to_id is not None:
        callback_data['id'] = to_id
    if text is None:
        btn_text = back_emoji
    else:
        btn_text = text
    return InlineKeyboardButton(btn_text,
                                callback_data=json.dumps(callback_data))


def settings_keyboard(contest_user: User):
    keyboard = InlineKeyboardMarkup(row_width=1)
    user_settings = TelegramUserSettings.objects.get(contest_user=contest_user)
    exclude = []
    meta = user_settings._meta
    if not (contest_user.is_staff or contest_user.is_superuser):
        exclude = ['questions', 'reports', 'submissions']
        goback_type = 'back'
    else:
        goback_type = 'staff_back'

    for setting in meta.get_fields():
        setting_name = setting.name
        setting_verbose_name = meta.get_field(field_name=setting_name).verbose_name
        if setting_name not in (['id', 'contest_user'] + exclude):
            keyboard.row(InlineKeyboardButton(text=setting_verbose_name,
                                              callback_data=json.dumps({'type': 'sett',
                                                                        'name': setting_name,
                                                                        'act': 'text'})),
                         InlineKeyboardButton(text=marks_emojis[getattr(user_settings, setting_name)],
                                              callback_data=json.dumps({'type': 'sett',
                                                                        'name': setting_name,
                                                                        'act': 'chg'})))
    keyboard.row(goback_button(goback_type=goback_type, to='courses'))
    return keyboard


def staff_start_keyboard(staff_contest_user: User):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_header = [f'{courses_emoji} Ваши курсы']
    table_list = Course.objects.filter(leaders__account=Account.objects.get(user=staff_contest_user))
    table_message_text = 'Курсы, в которых Вы являетесь лидером / одним из лидеров.'

    none_type_row(keyboard, table_header)
    for course in table_list:
        keyboard.row(InlineKeyboardButton(text=str(course), callback_data=json.dumps({'type': 'staff_go',
                                                                                      'to': 'course',
                                                                                      'id': course.id})))
    keyboard.row(InlineKeyboardButton(text=f'{user_settings_emoji} Настройки',
                                      callback_data=json.dumps({'type': 'get_settings'})))
    keyboard.row(InlineKeyboardButton(text=logout_btn_text,
                                      callback_data=json.dumps({'type': 'exit'})))
    return keyboard, table_message_text


def staff_course_menu_keyboard(course_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    course = Course.objects.get(pk=course_id)
    table_message_text = f'Курс <b>{course}</b>.\n\n' \
                         f'Справка:\n' \
                         f'{users_emoji} Успеваемость конкретного студента - позволяет посмотреть успеваемость по курсу у выбранного студента.\n' \
                         f'{problems_emoji} Успеваемость студентов по задачам - позволяет посмотреть общую успеваемость студентов по выбранной задаче.'

    keyboard.add(
        InlineKeyboardButton(text=f'{users_emoji} Успеваемость конкретного студента',
                             callback_data=json.dumps({'type': 'staff_go',
                                                       'to': 'course_students',
                                                       'id': course_id})),
        InlineKeyboardButton(text=f'{problems_emoji} Успеваемость студентов по задачам',
                             callback_data=json.dumps({'type': 'staff_go',
                                                       'to': 'contests',
                                                       'id': course_id}))
    )
    keyboard.add(goback_button(goback_type='staff_back', to='courses', to_id=course_id))
    return keyboard, table_message_text


def staff_course_students_keyboard(course_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    course = Course.objects.get(pk=course_id)
    all_course_users = Credit.objects.filter(course=course, score__lte=2).values_list('user')
    active_course_users = Account.objects.filter(user__in=all_course_users,
                                                 level__in=[course.level - 1, course.level, course.level + 1])

    table_message_text = f'Курс <b>{course}</b>.\n' \
                         f'Выберите студента, чтобы посмотреть его успеваемость.'
    for student in active_course_users:
        keyboard.add(InlineKeyboardButton(text=str(student), callback_data=json.dumps({'type': 'staff_go',
                                                                                       'to': 'stud',
                                                                                       'crs_id': course_id,
                                                                                       'stu_id': student.user.id})))
    keyboard.add(goback_button(goback_type='staff_back', to='course', to_id=course_id))
    return keyboard, table_message_text


def staff_course_student_menu_keyboard(course_id: int, student_id: int, show_submissions_number=False):
    keyboard = InlineKeyboardMarkup(row_width=1)
    student = User.objects.get(pk=student_id)
    course = Course.objects.get(pk=course_id)
    student_assignments_of_course = student.assignment_set.filter(problem__contest__course=course)
    contests_of_student_assignments = Contest.objects.filter(
        pk__in=student_assignments_of_course.values_list('problem__contest'))

    if show_submissions_number:
        none_type_row(keyboard, ['Задача', 'Оценка', 'Кол-во посылок'])
        check_emoji = checked_emoji
    else:
        none_type_row(keyboard, ['Задача', 'Оценка'])
        check_emoji = unchecked_emoji

    table_message_text = f'Курс <b>{course}</b>.\n' \
                         f'Студент <b>{Account.objects.get(user=student)}</b>.\n' \
                         f'Выберите задачу.'
    for contest in contests_of_student_assignments:
        keyboard.add(InlineKeyboardButton(text=f'{selection_emoji} {contest}',
                                          callback_data=json.dumps({'type': 'none'})))
        for problem_assignment in student_assignments_of_course.filter(problem__contest=contest):
            problem = problem_assignment.problem
            problem_row = [InlineKeyboardButton(text=f'{problem}',
                                                callback_data=json.dumps({'type': 'staff_go',
                                                                          'to': 'problem',
                                                                          'id': problem.id})),
                           score_button(score=problem_assignment.score,
                                        btn_url=f'{CONTEST_DOMAIN}{problem_assignment.get_absolute_url()}update?action=evaluate')]
            if show_submissions_number:
                problem_row.append(InlineKeyboardButton(text=str(len(problem_assignment.submission_set.all())),
                                                        url=f'{CONTEST_DOMAIN}{problem_assignment.get_absolute_url()}',
                                                        callback_data=json.dumps({'type': 'none'})))
            keyboard.row(*problem_row)

    keyboard.add(InlineKeyboardButton(text=f'{check_emoji} Показать посылки студента',
                                      callback_data=json.dumps({'type': 'stu_sett',
                                                                'crs_id': course_id,
                                                                'stu_id': student.id,
                                                                'cur_val': int(show_submissions_number)})))
    keyboard.add(goback_button(goback_type='staff_back', to='course_students', to_id=course_id))
    return keyboard, table_message_text


def staff_course_contests_keyboard(course_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    course = Course.objects.get(pk=course_id)
    contests = Contest.objects.filter(course=course)
    table_message_text = f'Курс <b>{course}</b>.\n' \
                         f'Выберите раздел.'
    for contest in contests:
        keyboard.add(InlineKeyboardButton(text=str(contest), callback_data=json.dumps({'type': 'staff_go',
                                                                                       'to': 'contest',
                                                                                       'id': contest.id})))
    keyboard.add(goback_button(goback_type='staff_back', to='course', to_id=course_id))
    return keyboard, table_message_text


def staff_course_problems_keyboard(contest_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    contest = Contest.objects.get(pk=contest_id)
    course = contest.course
    problems = Problem.objects.filter(contest=contest)
    table_message_text = f'Курс <b>{course}</b>.\n' \
                         f'Раздел <b>{contest}</b>.\n' \
                         f'Выберите задачу.'
    for problem in problems:
        keyboard.add(InlineKeyboardButton(text=str(problem), callback_data=json.dumps({'type': 'staff_go',
                                                                                       'to': 'problem',
                                                                                       'id': problem.id})))
    keyboard.add(goback_button(goback_type='staff_back', to='contests', to_id=course.id))
    return keyboard, table_message_text


def staff_problem_menu_keyboard(problem_id: int, show_submissions_number=True):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    course = problem.course
    contest = problem.contest
    all_course_users = Credit.objects.filter(course=course, score__lte=2).values_list('user')
    active_course_users = Account.objects.filter(user__in=all_course_users,
                                                 level__in=[course.level - 1, course.level, course.level + 1])

    students_assignment_with_problem = Assignment.objects.filter(problem_id=problem_id,
                                                                 user__in=active_course_users.values_list(
                                                                     'user')).order_by('user__last_name')
    students_with_problem = Account.objects.filter(
        user__in=students_assignment_with_problem.values_list('user')).order_by('user__last_name')
    if show_submissions_number:
        none_type_row(keyboard, ['Студент', 'Оценка', 'Кол-во посылок'])
        check_emoji = checked_emoji
    else:
        none_type_row(keyboard, ['Студент', 'Оценка'])
        check_emoji = unchecked_emoji

    if len(students_assignment_with_problem) == 0:
        keyboard.add(none_type_button(btn_text='Никому не назначена эта задача'))

    table_message_text = f'Курс <b>{course}</b>.\n' \
                         f'Раздел <b>{contest}</b>.\n' \
                         f'Задача <b>{problem}</b>.\n' \
                         f'Выберите студента.'
    for student, student_assignment in zip(students_with_problem, students_assignment_with_problem):
        student_row = [InlineKeyboardButton(text=str(student),
                                            callback_data=json.dumps({'type': 'staff_go',
                                                                      'to': 'stud',
                                                                      'crs_id': course.id,
                                                                      'stu_id': student.user.id})),
                       score_button(score=student_assignment.score,
                                    btn_url=f'{CONTEST_DOMAIN}{student_assignment.get_absolute_url()}update?action=evaluate')]
        if show_submissions_number:
            student_row.append(InlineKeyboardButton(text=str(len(student_assignment.submission_set.all())),
                                                    url=f'{CONTEST_DOMAIN}{student_assignment.get_absolute_url()}'))
        keyboard.row(*student_row)

    keyboard.add(InlineKeyboardButton(text=f'{check_emoji} Показать посылки студентов',
                                      callback_data=json.dumps({'type': 'prob_sett',
                                                                'prob_id': problem.id,
                                                                'cur_val': int(show_submissions_number)})))
    keyboard.add(goback_button(goback_type='staff_back', to='contest', to_id=contest.id))
    return keyboard, table_message_text


# TODO:
#  -3. Webhook deletion on server stopping !!!!
#  - LOCALHOST_DOMAIN перенести в common_settings.py
#  -2. что-то сделать с описанием задачи
#  -1. поддержка отображения расписания в формате PDF прямо на сайте
#  0. проверить, что будет при смене пароля через сайт (будет ли доступен функционал?)
#  1. problems list keyboard paginator
#  - возможность у преподавателей прослушать через бота голосовые сообщения
#  3. Submission deadline notification and connection with bot settings (user can set time interval for these type of notification)

def student_table_keyboard(table_type: str, contest_user: User, table_id: int = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_list = None
    table_title = None
    table_header = None
    back_btn = None
    table_message_text = None
    if table_type == 'courses':
        table_list = Credit.objects.filter(user=contest_user)
        table_title = [f'{courses_emoji} Ваши курсы']
        table_header = ['Курс', 'Оценка']
        table_message_text = 'Ваши курсы'
        back_btn = None
    elif table_type == 'contests':
        course = Course.objects.get(pk=table_id)
        table_list = Contest.objects.filter(pk__in=
                                            get_user_assignments(user=contest_user,
                                                                 course_id=table_id).values_list('problem__contest'))
        table_title = [f'{contest_emoji} {course}']
        table_header = ['Разделы']
        table_message_text = f'Курс "{course}"'
        back_btn = goback_button(goback_type='back', to='courses')
    elif table_type == 'problems':
        contest = Contest.objects.get(pk=table_id)
        table_list = get_user_assignments(user=contest_user, contest_id=table_id)
        table_title = [f'{contest_emoji} {contest}']
        table_header = ['Задача', 'Оценка']
        table_message_text = f'Раздел "{contest}"'
        back_btn = goback_button(goback_type='back', to='course', to_id=contest.course_id)

    none_type_row(keyboard, table_title)
    none_type_row(keyboard, table_header)
    if len(table_list) == 0:
        none_type_row(keyboard, ['Заданий нет'])

    if table_type == 'courses':
        for table_obj in table_list:
            keyboard.row(
                goback_button(goback_type='go', to=table_type[0:-1], to_id=table_obj.course.id, text=str(table_obj.course)),
                score_button(table_obj.score)
            )
    elif table_type == 'problems':
        for problem in table_list:
            keyboard.row(
                goback_button(goback_type='go', to=table_type[0:-1], to_id=problem.problem.id, text=str(problem.problem)),
                score_button(problem.score)
            )
    else:
        for contest in table_list:
            keyboard.row(goback_button(goback_type='go', to='contest', to_id=contest.id, text=str(contest)))

    if table_type == 'courses':
        keyboard.row(InlineKeyboardButton(text=f'{user_settings_emoji} Настройки',
                                          callback_data=json.dumps({'type': 'get_settings'})))
        keyboard.row(InlineKeyboardButton(text=logout_btn_text,
                                          callback_data=json.dumps({'type': 'exit'})))

    if back_btn is not None:
        keyboard.row(back_btn)
    return keyboard, table_message_text
# TODO:
#  student_table_keyboard разделить на разные функции


def problem_detail_keyboard(contest_user: User, problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    header = [f'{problem_emoji} {problem.title}']
    problem_comments = problem.comment_set.actual()
    description_btn = InlineKeyboardButton(text='Описание задачи', callback_data=json.dumps({'type': 'problem',
                                                                                             'item': 'description',
                                                                                             'id': problem_id}))
    submissions_btn = InlineKeyboardButton(text='Посылки к задаче', callback_data=json.dumps({'type': 'problem',
                                                                                              'item': 'submissions',
                                                                                              'id': problem_id}))
    discussion_btn = InlineKeyboardButton(text=f'Обсуждение задачи ({comments_emoji} {problem_comments.count()})'
                                          if problem_comments.count() != 0 else 'Обсуждение задачи',
                                          url=f'{CONTEST_DOMAIN}{problem.get_absolute_url()}discussion')
    back_btn = goback_button(goback_type='back', to='contest', to_id=problem.contest_id)

    none_type_row(keyboard, header)

    keyboard.add(description_btn, submissions_btn, discussion_btn)
    if Assignment.objects.get(user=contest_user, problem=problem).credit_incomplete and problem.type in ['Files', 'Verbal']:
        keyboard.add(
            InlineKeyboardButton(text=f'{send_emoji} Отправить решение', callback_data=json.dumps({'type': 'submission',
                                                                                                   'sub_type': problem.type,
                                                                                                   'id': problem_id})))
    keyboard.add(back_btn)
    return keyboard, f'Задача "{problem}"'


def submissions_list_keyboard(contest_user: User, problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    submissions_list = list(problem.submission_set.filter(assignment__user=contest_user))
    title = [f'{problem_emoji} {problem.title}. Посылки']
    header = ['Посылка', 'Статус'] if submissions_list else ['Посылок нет']
    none_type_row(keyboard, title)
    none_type_row(keyboard, header)
    locale.setlocale(locale.LC_TIME, "Russian")
    for submission in submissions_list:
        keyboard.row(InlineKeyboardButton(text=submission.date_created.strftime('%d %b %Y г. в %H:%M').lower(),
                                          url=f'{CONTEST_DOMAIN}{submission.get_absolute_url()}'),
                     InlineKeyboardButton(text=f'{submission_status_emojis[submission.status]} {submission.status}',
                                          callback_data=json.dumps({'type': 'status',
                                                                    'status_obj_id': submission.id})))

    keyboard.row(goback_button(goback_type='back', to='problem', to_id=problem_id))
    return keyboard


def submission_cancel_keyboard(problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(goback_button(goback_type='back', to='problem', to_id=problem_id))
    return keyboard


def submission_files_control_texts():
    return f'{checked_emoji} Готово', f'{cross_emoji} Отмена'


def submission_creation_keyboard():
    done_text, cancel_text = submission_files_control_texts()

    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(text=done_text), KeyboardButton(text=cancel_text))
    return keyboard, done_text, cancel_text


def notification_keyboard(obj):
    keyboard = InlineKeyboardMarkup(row_width=1)
    if obj is None:
        return None

    obj_id = obj.id
    if isinstance(obj, Course):
        button = goback_button(goback_type='go', to='course', to_id=obj_id, text='Перейти к курсу')
    elif isinstance(obj, Assignment):
        obj_id = obj.problem.id
        button = goback_button(goback_type='go', to='problem', to_id=obj_id, text='Перейти к задаче')
    elif isinstance(obj, Comment):
        button = InlineKeyboardButton(text='Перейти к комментарию', url=f'{CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Question):
        button = InlineKeyboardButton(text='Перейти к вопросу', url=f'{CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Report):
        button = InlineKeyboardButton(text='Перейти к сообщению об ошибке',
                                      url=f'{CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Submission):
        # TODO: разделение на переход к посылке у преподавателей и у студентов
        button = InlineKeyboardButton(text='Перейти к посылке',
                                      url=f'{CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Schedule):
        button = InlineKeyboardButton(text='Перейти к расписанию',
                                      url=f'{CONTEST_DOMAIN}{obj.get_absolute_url()}')
    else:
        return None

    keyboard.add(button)
    return keyboard


def timer_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton(text=hourglass_emoji))