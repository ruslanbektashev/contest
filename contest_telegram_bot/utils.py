import json
import re

from django.core.exceptions import ObjectDoesNotExist


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

    if not getattr(contest_recipient_settings, notification_obj_type):
        return

    notification_msg = f'{notification.subject.account} {notification.action} <b>{notification_obj}</b> ' \
                       f'{notification.relation if notification.relation is not None else ""} ' \
                       f'<b>{notification.reference if notification.reference is not None else ""}</b>'

    recipient_tg_chats = list(TelegramUser.objects.filter(contest_user=contest_recipient))

    from contest_telegram_bot.bot import tbot
    from contest_telegram_bot.keyboards import notification_keyboard
    for tg_chat in recipient_tg_chats:
        tbot.send_message(chat_id=tg_chat.chat_id, text=notification_msg,
                          reply_markup=notification_keyboard(obj=notification_obj), parse_mode='HTML')


def notify_all_specific_tg_users(notification_msg: str, tg_users, notification_obj=None):
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
        auth_fun_args: dict,
        unauth_fun_args: dict
):
    if get_telegram_user(chat_id=chat_id) is None:
        unauthorized_fun(**auth_fun_args)
    else:
        authorized_fun(**unauth_fun_args)


def json_get(json_str: str, key: str):
    return json.loads(json_str)[key]


def create_file_from_bytes(file_bytes: bytes, filename: str):
    with open(filename, 'wb') as new_file:
        new_file.write(file_bytes)


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


def file_extension(filename: str):
    return filename.split('.')[1]


def is_excel_file(filename: str):
    return re.search('xlsx*', file_extension(filename=filename))
