from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from accounts.models import Activity, Subscription
from contest.abstract import CRUDEntry

"""==================================================== Question ===================================================="""


class Question(CRUDEntry):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", verbose_name="Владелец")
    addressee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", verbose_name="Адресат")

    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(blank=True, verbose_name="Ответ")

    is_published = models.BooleanField(default=False, verbose_name="Опубликован?")
    redirect_comment = models.CharField(max_length=255, null=True, blank=True, verbose_name="Комментарий к переадресации")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created:
            Activity.objects.notify_user(self.addressee, subject=self.owner, action="задал вопрос", object=self)
        if not created:
            Activity.objects.notify_user(self.owner, subject=self, action="обновлен вопрос")

    def __str__(self):
        return "%s" % self.question


"""===================================================== Report ====================================================="""


class Report(CRUDEntry):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(blank=True, verbose_name="Сообщение")
    page_url = models.URLField(verbose_name="Откуда отправлено")
    closed = models.BooleanField(default=False, verbose_name="Закрыто")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Сообщение об ошибке"
        verbose_name_plural = "Сообщения об ошибках"

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created:
            user_ids = Subscription.objects.filter(object_type=ContentType.objects.get(model='report')).values_list('user', flat=True)
            Activity.objects.notify_users(user_ids, subject=self.owner, action="отправил сообщение об ошибке", object=self)
        if not created:
            Activity.objects.notify_user(self.owner, subject=self, action="обновлен статус сообщения")

    def __str__(self):
        return self.title or (str(self.text[:64]) + (str(self.text[64:]) and '...'))
