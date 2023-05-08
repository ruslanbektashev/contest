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
    comments = models.BooleanField(verbose_name='Комментарии', default=True)
    announcements = models.BooleanField(verbose_name='Объявления', default=True)
    schedules = models.BooleanField(verbose_name='Расписание', default=False)
    submissions = models.BooleanField(verbose_name='Отправленные посылки', default=False)
    submissions_mark = models.BooleanField(verbose_name='Оценки за посылки', default=True)
    assignments_mark = models.BooleanField(verbose_name='Оценки за задачи', default=True)
    courses_mark = models.BooleanField(verbose_name='Оценки за курсы', default=True)
    questions = models.BooleanField(verbose_name='Вопросы', default=True)
    reports = models.BooleanField(verbose_name='Сообщения об ошибках', default=True)
    assignments = models.BooleanField(verbose_name='Назначение задач', default=True)

    class Meta:
        verbose_name = "Настройки телеграм-пользователя"
