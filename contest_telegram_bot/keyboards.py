import json
import re

from django.contrib.auth.models import User
from emoji import emojize
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from accounts.models import Account, Comment
from django.conf import settings
from contest_telegram_bot.constants import user_settings_emoji, \
    logout_btn_text, submission_status_emojis, login_btn_text, send_emoji, comments_emoji, \
    marks_emojis, problems_emoji, users_emoji, selection_emoji, checked_emoji, unchecked_emoji, \
    cross_emoji, hourglass_emoji, back_emoji, plus_emoji, loudspeaker_emoji, \
    drop_down_list_emojis, little_white_square_emoji
from contest_telegram_bot.models import TelegramUserSettings
from contest_telegram_bot.utils import get_user_assignments, date_to_str, back_to_submissions_text, \
    get_active_course_users, send_notification_text, cancel_notification_text, get_all_faculties_without_mfk, \
    get_all_study_levels, notify_settings_students_faculties_to_bool, problem_deadline_expired
from contests.models import Course, Contest, Problem, Assignment, Submission, Credit
from schedule.models import Schedule
from support.models import Question, Report


def start_keyboard_unauthorized():
    login_btn = KeyboardButton(login_btn_text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(login_btn)
    return keyboard


def none_type_row(keyboard: InlineKeyboardMarkup, titles: list):
    if titles is not None and titles != []:
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
        score_choices = Credit.SCORE_CHOICES
        score_value = score_choices[len(score_choices) - score - 1*(score == 0)][1]
        return InlineKeyboardButton(text=emojize(f':keycap_{str(score)}:') if score > 0 else '-',
                                    url=btn_url,
                                    callback_data=json.dumps({'type': 'score',
                                                              'value': score_value}, ensure_ascii=False))
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


def make_notification_button(creator: str, course_id: int = None):
    if course_id is None:
        recipients_word = 'пользователям'
    else:
        recipients_word = 'студентам курса'
    return InlineKeyboardButton(text=f'{loudspeaker_emoji} Сделать рассылку {recipients_word}',
                                callback_data=json.dumps({'type': 'notify',
                                                          'creator': creator,
                                                          'course_id': course_id}))


def settings_keyboard(contest_user: User):
    keyboard = InlineKeyboardMarkup(row_width=1)
    contest_user_account = Account.objects.get(user=contest_user)
    user_settings = TelegramUserSettings.objects.get(contest_user=contest_user)
    text = f'Настройки оповещений пользователя {contest_user_account}.'

    exclude = []
    meta = user_settings._meta
    if not (contest_user_account.type == 2 or contest_user_account.type == 3):
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
    return keyboard, text


def staff_and_moders_start_keyboard(staff_contest_user: User, for_moders=False):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_list = Course.objects.filter(leaders__account=Account.objects.get(user=staff_contest_user))
    table_message_text = 'Курсы, в которых Вы являетесь лидером / одним из лидеров.'

    for course in table_list:
        keyboard.row(InlineKeyboardButton(text=str(course), callback_data=json.dumps({'type': 'staff_go',
                                                                                      'to': 'course',
                                                                                      'id': course.id})))
    if len(table_list) == 0:
        keyboard.row(none_type_button(btn_text='Нет курсов'),
                     InlineKeyboardButton(text=plus_emoji, url=f'{settings.CONTEST_DOMAIN}/course/create'))
    if for_moders:
        keyboard.add(make_notification_button(creator='moder'))
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
                         f'{problems_emoji} Успеваемость студентов по задачам - позволяет посмотреть общую успеваемость студентов по выбранной задаче.\n' \
                         f'{loudspeaker_emoji} Сделать рассылку студентам курса - позволяет отправить сообщение всем студентам курса'

    keyboard.add(
        InlineKeyboardButton(text=f'{users_emoji} Успеваемость конкретного студента',
                             callback_data=json.dumps({'type': 'staff_go',
                                                       'to': 'course_students',
                                                       'id': course_id})),
        InlineKeyboardButton(text=f'{problems_emoji} Успеваемость студентов по задачам',
                             callback_data=json.dumps({'type': 'staff_go',
                                                       'to': 'contests',
                                                       'id': course_id})),
        make_notification_button(creator='staff', course_id=course_id),
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
                                        btn_url=f'{settings.CONTEST_DOMAIN}{problem_assignment.get_absolute_url()}update?action=evaluate')]
            if show_submissions_number:
                if problem.type in ['Files', 'Verbal']:
                    callback_data = json.dumps({'type': 'subm_lst',
                                                'from': 'stud',
                                                'id': problem.id,
                                                'stud_id': student.id})
                    url = None
                else:
                    callback_data = None
                    url = f'{settings.CONTEST_DOMAIN}{problem_assignment.get_absolute_url()}'
                problem_row.append(InlineKeyboardButton(text=str(len(problem_assignment.submission_set.all())),
                                                        callback_data=callback_data,
                                                        url=url))
            keyboard.row(*problem_row)

    if len(contests_of_student_assignments) == 0:
        keyboard.add(none_type_button(btn_text='Задач нет.'))
    else:
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
    active_course_accounts, _ = get_active_course_users(course_id=course.id)

    students_assignment_with_problem = Assignment.objects.filter(problem_id=problem_id,
                                                                 user__in=active_course_accounts.values_list(
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
                                    btn_url=f'{settings.CONTEST_DOMAIN}{student_assignment.get_absolute_url()}update?action=evaluate')]
        if show_submissions_number:
            if problem.type in ['Files', 'Verbal']:
                callback_data = json.dumps({'type': 'subm_lst',
                                            'from': 'prob',
                                            'id': problem.id,
                                            'stud_id': student.user.id})
                url = None
            else:
                callback_data = None
                url = f'{settings.CONTEST_DOMAIN}{student_assignment.get_absolute_url()}'
            student_row.append(InlineKeyboardButton(text=str(len(student_assignment.submission_set.all())),
                                                    callback_data=callback_data, url=url))
        keyboard.row(*student_row)

    keyboard.add(InlineKeyboardButton(text=f'{check_emoji} Показать посылки студентов',
                                      callback_data=json.dumps({'type': 'prob_sett',
                                                                'prob_id': problem.id,
                                                                'cur_val': int(show_submissions_number)})))
    keyboard.add(goback_button(goback_type='staff_back', to='contest', to_id=contest.id))
    return keyboard, table_message_text


def staff_notification_initial_keyboard(course_id: int):
    text = f'Отправьте сообщение для студентов курса <b>{Course.objects.get(pk=course_id)}</b>.'
    keyboard = InlineKeyboardMarkup(row_width=1).add(goback_button(goback_type='staff_back',
                                                                   to='course', to_id=course_id))
    return keyboard, text


def moderator_notification_initial_keyboard(notification_settings: dict):
    def some_students_faculty_is_open():
        for fac in all_faculties:
            if to_students["faculties"][fac.id]["open"]:
                return True
        return False

    text = f'Выберите группу людей, а затем отправьте сообщение с текстом оповещения.\n\n' \
           f'<b>Справка:</b>\n' \
           f'Нажмите на {drop_down_list_emojis[0]}, чтобы уточнить факультет/группу оповещаемых пользователей.'
    keyboard = InlineKeyboardMarkup(row_width=1)
    all_faculties = get_all_faculties_without_mfk()
    all_levels = get_all_study_levels()

    to_moderators = notification_settings['moders']
    to_staff = notification_settings['staff']
    to_students = notification_settings['stu']
    to_moderators_bool = int(bool(to_moderators['faculties']))
    to_staff_bool = int(bool(to_staff['faculties']))
    to_students_bool = notify_settings_students_faculties_to_bool(to_students['faculties'])

    open_moderator_options = to_moderators['open']
    open_staff_options = to_staff['open']
    open_students_options = to_students['open']
    check_emoji = marks_emojis
    list_emojis = drop_down_list_emojis

    moderators_button = InlineKeyboardButton(text=f'{check_emoji[to_moderators_bool]} Модераторам',
                                             callback_data=json.dumps({'type': 'n_set.set',
                                                                       'obj': 'moders'}))
    staff_button = InlineKeyboardButton(text=f'{check_emoji[to_staff_bool]} Преподавателям',
                                        callback_data=json.dumps({'type': 'n_set.set',
                                                                  'obj': 'staff'}))
    students_button = InlineKeyboardButton(text=f'{check_emoji[to_students_bool]} Студентам',
                                           callback_data=json.dumps({'type': 'n_set.set',
                                                                     'obj': 'stu'}))
    moderators_options_button = InlineKeyboardButton(text=f'{list_emojis[open_moderator_options]}',
                                                     callback_data=json.dumps({'type': 'n_set.opn',
                                                                               'obj': 'moders'}))
    staff_options_button = InlineKeyboardButton(text=f'{list_emojis[open_staff_options]}',
                                                callback_data=json.dumps({'type': 'n_set.opn',
                                                                          'obj': 'staff'}))
    students_options_button = InlineKeyboardButton(text=f'{list_emojis[open_students_options]}',
                                                   callback_data=json.dumps({'type': 'n_set.opn',
                                                                             'obj': 'stu'}))
    if not some_students_faculty_is_open():
        keyboard.row(moderators_options_button, moderators_button)
        if to_moderators['open']:
            for faculty in all_faculties:
                cur_faculty_check_emoji = check_emoji[faculty.id in to_moderators["faculties"]]
                keyboard.row(none_type_button(btn_text=f'{little_white_square_emoji}'),
                             InlineKeyboardButton(text=f'{cur_faculty_check_emoji} {faculty}',
                                                  callback_data=json.dumps({'type': 'n_set.set',
                                                                            'obj': 'moders.fac',
                                                                            'f_id': faculty.id}))
                             )
        keyboard.row(none_type_button(btn_text=f'{little_white_square_emoji}'))
        keyboard.row(staff_options_button, staff_button)
        if to_staff['open']:
            for faculty in all_faculties:
                cur_faculty_check_emoji = check_emoji[faculty.id in to_staff["faculties"]]
                keyboard.row(none_type_button(btn_text=f'{little_white_square_emoji}'),
                             InlineKeyboardButton(text=f'{cur_faculty_check_emoji} {faculty}',
                                                  callback_data=json.dumps({'type': 'n_set.set',
                                                                            'obj': 'staff.fac',
                                                                            'f_id': faculty.id}))
                             )
        keyboard.row(none_type_button(btn_text=f'{little_white_square_emoji}'))
        keyboard.row(students_options_button, students_button)
    if to_students['open']:
        for faculty in all_faculties:
            cur_faculty_check_emoji = check_emoji[int(bool(to_students["faculties"][faculty.id]['levels']))]
            cur_faculty_open = to_students["faculties"][faculty.id]["open"]
            cur_faculty_options_emoji = list_emojis[cur_faculty_open]

            keyboard.row(InlineKeyboardButton(
                             text=f'{cur_faculty_options_emoji}',
                             callback_data=json.dumps({'type': 'n_set.opn',
                                                       'obj': 'stu.fac',
                                                       'f_id': faculty.id})),
                         InlineKeyboardButton(text=f'{cur_faculty_check_emoji} {faculty}',
                                              callback_data=json.dumps({'type': 'n_set.set',
                                                                        'obj': 'stu.fac',
                                                                        'f_id': faculty.id}))
                         )
            if cur_faculty_open:
                for level in all_levels:
                    if level[0] % 2:
                        cur_faculty_level_check_emoji = check_emoji[int(bool(level[0] in to_students["faculties"][faculty.id]['levels']))]
                        level_name = re.sub(', (?:(I.*)|(V.*)) семестр', '', level[1])
                        keyboard.row(none_type_button(btn_text=f'{little_white_square_emoji}'),
                                     InlineKeyboardButton(text=f'{cur_faculty_level_check_emoji} {level_name}',
                                                          callback_data=json.dumps({'type': 'n_set.set',
                                                                                    'obj': 'stu.fac.l',
                                                                                    'f_id': faculty.id,
                                                                                    'l_id': level[0]}))
                                     )
            if cur_faculty_open:
                keyboard.row(none_type_button(btn_text=f'{little_white_square_emoji}'),
                             none_type_button(btn_text=f'{little_white_square_emoji}'),
                             )

    keyboard.add(goback_button(goback_type='staff_back',
                               to='courses', text=f'{cross_emoji} Отмена'))
    return keyboard, text


def notification_control_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        KeyboardButton(text=send_notification_text),
        KeyboardButton(text=cancel_notification_text)
    )
    return keyboard


# TODO:
#  1. Submission deadline notification and connection with bot settings (user can set time interval for
#  these type of notification)

def student_table_keyboard(contest_user: User, table_type: str, table_id: int = None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    table_list = None
    table_header = None
    back_btn = None
    table_message_text = None
    if table_type == 'courses':
        table_list = Credit.objects.filter(user=contest_user)
        table_header = ['Курс', 'Оценка']
        table_message_text = 'Ваши курсы'
        back_btn = None
    elif table_type == 'contests':
        course = Course.objects.get(pk=table_id)
        table_list = Contest.objects.filter(pk__in=
                                            get_user_assignments(user=contest_user,
                                                                 course_id=table_id).values_list('problem__contest'))
        table_message_text = f'Курс <b>{course}</b>.\nРазделы'
        back_btn = goback_button(goback_type='back', to='courses')
    elif table_type == 'problems':
        contest = Contest.objects.get(pk=table_id)
        table_list = get_user_assignments(user=contest_user, contest_id=table_id)
        table_header = ['Задача', 'Оценка']
        table_message_text = f'Раздел <b>{contest}</b>.\n\nСправка:\n' \
                             f'Символом {send_emoji} отмечены задачи, к которым можно отправить посылки через телеграм.'
        back_btn = goback_button(goback_type='back', to='course', to_id=contest.course_id)

    none_type_row(keyboard, table_header)
    if len(table_list) == 0:
        none_type_row(keyboard, ['Заданий нет'])

    if table_type == 'courses':
        for table_obj in table_list:
            keyboard.row(
                goback_button(goback_type='go', to=table_type[0:-1], to_id=table_obj.course.id,
                              text=str(table_obj.course)),
                score_button(table_obj.score)
            )
    elif table_type == 'problems':
        for problem_assignment in table_list:
            if problem_deadline_expired(contest_user=contest_user, problem_id=problem_assignment.problem_id):
                problem_score = problem_assignment.score
            else:
                problem_score = 0

            if problem_assignment.problem.type in ['Verbal', 'Files']:
                btn_text = f'{send_emoji} {str(problem_assignment.problem)}'
            else:
                btn_text = str(problem_assignment.problem)

            keyboard.row(
                goback_button(goback_type='go', to=table_type[0:-1], to_id=problem_assignment.problem.id,
                              text=btn_text),
                score_button(problem_score)
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


def problem_detail_keyboard(contest_user: User, problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    problem_comments = problem.comment_set.actual()
    submissions_btn = InlineKeyboardButton(text='Посылки к задаче', callback_data=json.dumps({'type': 'problem',
                                                                                              'item': 'submissions',
                                                                                              'id': problem_id}))
    discussion_btn = InlineKeyboardButton(text=f'Обсуждение задачи ({comments_emoji} {problem_comments.count()})'
                                          if problem_comments.count() != 0 else 'Обсуждение задачи',
                                          url=f'{settings.CONTEST_DOMAIN}{problem.get_absolute_url()}discussion')
    back_btn = goback_button(goback_type='back', to='contest', to_id=problem.contest_id)

    keyboard.add(submissions_btn, discussion_btn)
    if Assignment.objects.get(user=contest_user, problem=problem).credit_incomplete:
        if problem.type in ['Files', 'Verbal']:
            callback_data = json.dumps({'type': 'submission',
                                        'sub_type': problem.type,
                                        'id': problem_id})
            url = None
        else:
            callback_data = None
            url = f'{settings.CONTEST_DOMAIN}{problem.get_absolute_url()}submission/create'
        keyboard.add(
            InlineKeyboardButton(text=f'{send_emoji} Отправить решение', callback_data=callback_data, url=url))
    keyboard.add(back_btn)
    return keyboard, f'Задача "{problem}"'


def submissions_list_keyboard(contest_user: User, problem_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)
    problem = Problem.objects.get(pk=problem_id)
    submissions_list = problem.submission_set.filter(assignment__user=contest_user)
    header = ['Посылка', 'Статус'] if submissions_list else ['Посылок нет']
    none_type_row(keyboard, header)
    for submission in submissions_list:
        if problem.type in ['Files', 'Verbal']:
            callback_data = json.dumps({'type': 'submission_detail',
                                        'id': submission.id})
            url = None
        else:
            callback_data = None
            url = f'{settings.CONTEST_DOMAIN}{submission.get_absolute_url()}'

        if problem_deadline_expired(contest_user=contest_user, problem_id=problem_id):
            submission_status = submission.status
        else:
            submission_status = 'UN'
        keyboard.row(InlineKeyboardButton(text=date_to_str(date=submission.date_created),
                                          callback_data=callback_data,
                                          url=url),
                     InlineKeyboardButton(text=f'{submission_status_emojis[submission_status]} {submission_status}',
                                          callback_data=json.dumps({'type': 'status',
                                                                    'status_obj_id': submission.id})))
    return keyboard


def submissions_list_keyboard_for_students(contest_user: User, problem_id: int):
    submissions_list = submissions_list_keyboard(contest_user=contest_user, problem_id=problem_id)
    submissions_list.add(goback_button(goback_type='back', to='problem', to_id=problem_id))
    return submissions_list


def submissions_list_keyboard_for_staff(contest_user: User, problem_id: int, back_to: str):
    problem = Problem.objects.get(pk=problem_id)
    submissions_list = submissions_list_keyboard(contest_user=contest_user, problem_id=problem_id)
    if back_to == 'stud':
        submissions_list.add(InlineKeyboardButton(text=back_emoji, callback_data=json.dumps({'type': 'staff_go',
                                                                                             'to': 'stud',
                                                                                             'crs_id': problem.course.id,
                                                                                             'stu_id': contest_user.id})))
    else:
        submissions_list.add(goback_button(goback_type='staff_back', to='problem', to_id=problem_id))
    return submissions_list, f'Курс <b>{problem.course}</b>.\n' \
                             f'Раздел <b>{problem.contest}</b>.\n' \
                             f'Задача <b>{problem}</b>.\n' \
                             f'Посылки студента <b>{Account.objects.get(user=contest_user)}</b>.'


def back_to_problem_keyboard(problem_id: int):
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
        button = InlineKeyboardButton(text='Перейти к комментарию', url=f'{settings.CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Question):
        button = InlineKeyboardButton(text='Перейти к вопросу', url=f'{settings.CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Report):
        button = InlineKeyboardButton(text='Перейти к сообщению об ошибке',
                                      url=f'{settings.CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Submission):
        button = InlineKeyboardButton(text='Перейти к посылке',
                                      url=f'{settings.CONTEST_DOMAIN}{obj.get_absolute_url()}')
    elif isinstance(obj, Schedule):
        button = InlineKeyboardButton(text='Перейти к расписанию',
                                      url=f'{settings.CONTEST_DOMAIN}{obj.get_absolute_url()}')
    else:
        return None

    keyboard.add(button)
    return keyboard


def back_to_submissions_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton(text=back_to_submissions_text))


def timer_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton(text=hourglass_emoji))
