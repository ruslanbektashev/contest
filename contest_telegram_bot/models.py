from django.contrib.auth.models import User
from django.db import models


class TelegramEntity(models.Model):
    chat_id = models.BigIntegerField(verbose_name="ID телеграм-сущности")

    class Meta:
        abstract = True


class TelegramUser(TelegramEntity):
    contest_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Пользователь на Контесте")

    class Meta:
        verbose_name = "Пользователь в телеграме"


class TelegramUserSettings(models.Model):
    contest_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Пользователь на Контесте")
    comments = models.BooleanField(verbose_name='Оповещения о комментариях', default=True)
    announcements = models.BooleanField(verbose_name='Оповещения об объявлениях', default=True)
    schedules = models.BooleanField(verbose_name='Оповещения о расписании', default=False)
    submissions = models.BooleanField(verbose_name='Оповещения об отправляемых посылках', default=False)
    submissions_mark = models.BooleanField(verbose_name='Оповещения об оценке за посылки', default=True)
    assignments_mark = models.BooleanField(verbose_name='Оповещения об оценке за задачи', default=True)
    courses_mark = models.BooleanField(verbose_name='Оповещения об оценке за курс', default=True)
    questions = models.BooleanField(verbose_name='Оповещения о вопросах', default=True)
    reports = models.BooleanField(verbose_name='Оповещения о сообщениях об ошибках', default=True)
    assignments = models.BooleanField(verbose_name='Оповещения о назначениях задач', default=True)

    class Meta:
        verbose_name = "Настройки телеграм-пользователя"
