from django.core.exceptions import ObjectDoesNotExist
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from accounts.models import Account
from contest_telegram_bot.constants import help_btn_text, login_btn_text, logout_btn_text

from contest_telegram_bot.models import TelegramUser


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
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(login_btn, help_btn)
    return keyboard


def start_keyboard_non_authorized():
    login_btn = KeyboardButton(login_btn_text)
    help_btn = KeyboardButton(help_btn_text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True).add(login_btn, help_btn)
    return keyboard