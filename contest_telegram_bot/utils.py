import json
import locale

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from emoji import emojize
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from accounts.models import Account
from contest_telegram_bot.constants import help_btn_text, login_btn_text, logout_btn_text, courses_emoji, contest_emoji, \
    bot_settings_emoji, user_settings_emoji, problem_emoji, submission_status_emojis

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
