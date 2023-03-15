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

# class TelegramGroup(TelegramEntity):
#     contest_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь на Контесте")
#
#     class Meta:
#         verbose_name = "Группа в телеграме"
