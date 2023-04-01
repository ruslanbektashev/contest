import json
import re

from django.core.exceptions import ObjectDoesNotExist


from contest_telegram_bot.models import TelegramUser


def get_telegram_user(chat_id: int):
    try:
        return TelegramUser.objects.get(chat_id=chat_id)
    except ObjectDoesNotExist:
        return None


def notify_tg_users(notification):
    contest_recipient = notification.recipient
    recipient_tg_chats = list(TelegramUser.objects.filter(contest_user=contest_recipient))
    notification_obj = notification.object
    notification_msg = f'{notification.subject.account} {notification.action} <b>{notification_obj}</b> ' \
                       f'{notification.relation if notification.relation is not None else ""} ' \
                       f'<b>{notification.reference if notification.reference is not None else ""}</b>'
    print(type(notification.object))
    for tg_chat in recipient_tg_chats:
        from contest_telegram_bot.bot import tbot
        from contest_telegram_bot.keyboards import notification_keyboard
        tbot.send_message(chat_id=tg_chat.chat_id, text=notification_msg,
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


def is_schedule_file(filename: str):
    return re.search('([Р-р]асписание)|(янв(ар)*|февр*(ал)*|апр(ел)*|июн|июл|сент*(ябр)*|окт(ябр)*|ноя(бр)*|дек(абр)*)[ь-я]*|(марта*)|(ма[й-я])', filename)


def file_extension(filename: str):
    return filename.split('.')[1]


def is_excel_file(filename: str):
    return re.search('xlsx*', file_extension(filename=filename))
