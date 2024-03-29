import json
import locale
import re

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from contest_telegram_bot.constants import filled_progress_emoji, empty_progress_emoji, back_emoji, loudspeaker_emoji, \
    cross_emoji
from contest_telegram_bot.models import TelegramUser, TelegramUserSettings


def get_telegram_user(chat_id: int):
    try:
        return TelegramUser.objects.get(chat_id=chat_id)
    except ObjectDoesNotExist:
        return None


def get_contest_user_by_tg_id(chat_id: int):
    tg_user = get_telegram_user(chat_id=chat_id)
    if tg_user is not None:
        return tg_user.contest_user
    else:
        return None


def get_user_assignments(user: User, course_id: int = None, contest_id: int = None, problem_id: int = None):
    from contests.models import Assignment
    user_assignment = Assignment.objects.filter(user=user)
    if course_id is None and contest_id is None and problem_id is None:
        return user_assignment
    if problem_id is not None:
        return user_assignment.get(problem_id=problem_id)
    if course_id is not None:
        return user_assignment.filter(problem__contest__course_id=course_id)
    if contest_id is not None:
        return user_assignment.filter(problem__contest_id=contest_id)


def get_user_submission_set_of_problem(user: User, problem_id: int):
    return get_user_assignments(user=user, problem_id=problem_id).submission_set.all()


def check_submission_limit_excess(user: User, problem_id: int):
    return len(get_user_submission_set_of_problem(user=user, problem_id=problem_id)) >= \
           get_user_assignments(user=user, problem_id=problem_id).submission_limit


def problem_deadline_expired(contest_user: User, problem_id: int):
    user_problem_assignment = get_user_assignments(user=contest_user, problem_id=problem_id)
    return (user_problem_assignment.deadline is None) or \
           (user_problem_assignment.deadline is not None and user_problem_assignment.deadline < timezone.now())


def notify_tg_users(notification):
    print(type(notification.object))
    contest_recipient = notification.recipient
    try:
        contest_recipient_settings = TelegramUserSettings.objects.get(contest_user=contest_recipient)
    except ObjectDoesNotExist:
        return

    notification_obj = notification.object
    notification_obj_type = str(type(notification_obj)).split('.')[-1].lower()[:-2] + 's'
    if 'оценку' in notification.action:
        notification_obj_type += '_mark'

    try:
        if not getattr(contest_recipient_settings, notification_obj_type):
            return
    except AttributeError:
        pass

    notification_msg = f'{notification.subject.account} {notification.action} <b>{notification_obj}</b> ' \
                       f'{notification.relation if notification.relation is not None else ""} ' \
                       f'<b>{notification.reference if notification.reference is not None else ""}</b>'

    recipient_tg_chats = list(TelegramUser.objects.filter(contest_user=contest_recipient))

    from contest_telegram_bot.bot import tbot
    from contest_telegram_bot.keyboards import notification_keyboard
    for tg_chat in recipient_tg_chats:
        tbot.send_message(chat_id=tg_chat.chat_id, text=notification_msg,
                          reply_markup=notification_keyboard(obj=notification_obj), parse_mode='HTML')


def notify_specific_tg_users(notification_msg: str, tg_users, notification_obj=None):
    if notification_obj is not None:
        notification_obj_type = str(type(notification_obj)).split('.')[-1].lower()[:-2] + 's'

    from contest_telegram_bot.bot import tbot
    from contest_telegram_bot.keyboards import notification_keyboard
    for tg_user in tg_users:
        if notification_obj is not None:
            if not getattr(TelegramUserSettings.objects.get(contest_user=tg_user.contest_user), notification_obj_type):
                continue
        tbot.send_message(chat_id=tg_user.chat_id, text=notification_msg,
                          reply_markup=notification_keyboard(obj=notification_obj), parse_mode='HTML')


def notify_specific_tg_users_by_contest_users(notification_msg: str, contest_users):
    tg_users = TelegramUser.objects.filter(contest_user__in=contest_users)
    notify_specific_tg_users(notification_msg=notification_msg, tg_users=tg_users)


def get_active_course_users(course_id: int):
    from contests.models import Credit, Course
    from accounts.models import Account
    course = Course.objects.get(pk=course_id)
    all_course_users = Credit.objects.filter(course=course, score__lte=2).values_list('user')
    active_course_accounts = Account.objects.filter(user__in=all_course_users,
                                                    level__in=[course.level - 1, course.level, course.level + 1])
    active_course_users = User.objects.filter(pk__in=active_course_accounts.values_list('user'))
    return active_course_accounts, active_course_users


def get_account_by_tg_id(chat_id: int):
    try:
        tg_user = TelegramUser.objects.get(chat_id=chat_id)
        from accounts.models import Account
        return Account.objects.get(user=tg_user.contest_user)
    except ObjectDoesNotExist:
        return None


def telegram_user_unauthorized(chat_id: int):
    tg_user = get_telegram_user(chat_id)
    if tg_user is not None:
        if tg_user.contest_user is None:
            return True
    return False


def tg_authorisation_wrapper(
        chat_id: int,
        authorized_fun,
        unauthorized_fun,
        auth_fun_args: dict = {},
        unauth_fun_args: dict = {}
):
    if get_telegram_user(chat_id=chat_id) is None:
        unauthorized_fun(**auth_fun_args)
    else:
        authorized_fun(**unauth_fun_args)


def all_content_types_with_exclude(exclude: list = []):
    all_content_types = ['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location',
                         'contact', 'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo',
                         'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
                         'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message', 'web_app_data']
    return list(filter(lambda x: x not in exclude, all_content_types))


def progress_bar(loaded_chunks: int, total_chunks: int):
    result_progress_bar = ''
    for _ in range(loaded_chunks):
        result_progress_bar += filled_progress_emoji
    for _ in range(loaded_chunks, total_chunks):
        result_progress_bar += empty_progress_emoji
    return result_progress_bar


def get_all_faculties_without_mfk():
    from django.db.models import Q
    from accounts.models import Faculty
    return Faculty.objects.filter(~Q(short_name='МФК'))


def get_all_faculties_without_mfk__ids():
    return list(get_all_faculties_without_mfk().values_list('pk', flat=True))


def get_all_study_levels():
    from accounts.models import Account
    return Account.LEVEL_CHOICES


def get_all_study_levels__ids():
    return [row[0] for row in get_all_study_levels()]


def notify_settings_students_faculties_to_bool(settings_students_faculties):
    for students_faculties_value in settings_students_faculties.values():
        if len(students_faculties_value['levels']) != 0:
            return 1
    return 0


def date_to_str(date):
    locale.setlocale(locale.LC_TIME, "Russian")
    return date.strftime('%d %b %Y г. в %H:%M').lower()


def json_get(json_str: str, key: str):
    return json.loads(json_str)[key]


def create_file_from_bytes(file_bytes: bytes, filename: str):
    with open(filename, 'wb') as new_file:
        new_file.write(file_bytes)


def filesize_to_text(filesize_in_bytes: int):
    if filesize_in_bytes < 1024:
        size_coeff = 1
        size_word = 'Б'
    elif 1024 <= filesize_in_bytes < (1024 * 1024):
        size_coeff = 1024
        size_word = 'КБ'
    else:
        size_coeff = 1024 * 1024
        size_word = 'МБ'
    return f'{(filesize_in_bytes / size_coeff):.2f}' + ' ' + size_word


def file_chunk_size(filesize: int):
    if filesize <= 256 * 1024:
        return None
    elif 256 * 1024 < filesize <= 1024 * 1024:
        return 256 * 1024
    elif 1024 * 1024 < filesize <= 5 * 1024 * 1024:
        return 768 * 1024
    else:
        return 1024 * 1024


def file_extension(filename: str):
    return '.' + filename.split('.')[-1]


def is_schedule_file(filename: str):
    return re.search('([Р-р]асписание)|((?:[Я-я]нв(ар)*|[Ф-ф]евр*(ал)*|[А-а]пр(ел)*|[И-и]юн|[И-и]юл|[С-с]ент*(ябр)*|[О-о]кт(ябр)*|[Н-н]оя(бр)*|[Д-д]ек(абр)*)[ь-я]*)|([М-м]ар(та*)*)|([М-м]а[й-я])', filename)


def get_course_label(pdf_content: str):
    courses = [
        'Прикладная математика и информатика',
        'Психология',
        'Реклама и связи с общественностью',
        'Филология',
        'ПМиИ'
    ]
    courses_regex = '(?:% s)' % '|'.join(courses)
    if len(re.findall("[мМ][аА][гГ][иИ][сС][тТ][рР][аА][тТ][уУ][рР][аА]", pdf_content)) == 0:
        return re.findall(f"{courses_regex}.*[1-5] курс", pdf_content)[0]
    else:
        magistracy_label = 'Магистратура'
        magistracy_part = re.search(f"({courses_regex}.*[1-2] курс)|([1-2] курс)", pdf_content).group()
        if re.search("-МО", pdf_content) is not None:
            magistracy_label += ' МО'
        magistracy_label += f' {magistracy_part}'
        return magistracy_label


def is_excel_file(filename: str):
    return re.search('xlsx*', file_extension(filename=filename))


back_to_submissions_text = f'{back_emoji} Вернуться к посылкам'
send_notification_text = f'{loudspeaker_emoji} Отправить'
cancel_notification_text = f'{cross_emoji} Отмена'
