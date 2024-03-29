from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from accounts.models import Comment, Notification
from contest.abstract import CRUDEntry

"""==================================================== Question ===================================================="""


class Question(CRUDEntry):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", verbose_name="Владелец")
    addressee = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="+",
                                  verbose_name="Адресат")

    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(blank=True, verbose_name="Ответ")

    is_published = models.BooleanField(default=False, verbose_name="Опубликовать", help_text="Опубликованный ответ "
                                                                                             "виден всем пользователям")
    redirect_comment = models.CharField(max_length=255, null=True, blank=True, verbose_name="Комментарий адресату")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created and self.addressee:
            Notification.objects.notify(self.addressee, subject=self.owner, action="задал вопрос", object=self)
        if not created and self.answer:
            Notification.objects.notify(self.owner, subject=self, action="обновлен")

    def __str__(self):
        return self.question


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
            user_ids = User.objects.filter(is_superuser=True).values_list('id', flat=True)
            Notification.objects.notify(user_ids, subject=self.owner, action="отправил сообщение об ошибке", object=self)
        if not created and self.closed:
            Notification.objects.notify(self.owner, subject=self, action="обновлен статус сообщения")

    def __str__(self):
        return self.title or (str(self.text[:64]) + (str(self.text[64:]) and '...'))


"""=================================================== Discussion ==================================================="""


class Discussion(CRUDEntry):
    topic = models.CharField(max_length=100, verbose_name="Тема")

    comment_set = GenericRelation(Comment, content_type_field='object_type')

    class Meta:
        verbose_name = "Обсуждение"
        verbose_name_plural = "Обсуждения"

    def get_discussion_url(self):
        return self.get_absolute_url()

    def __str__(self):
        return self.topic


"""================================================ TutorialStepPass ================================================"""


class TutorialStepPassQuerySet(models.QuerySet):
    def is_step_passed(self, user, view, step):
        return self.filter(user=user, view=view).filter(models.Q(step='__all__') | models.Q(step=step)).exists()


class TutorialStepPass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    view = models.CharField(max_length=100, verbose_name="Вью")
    step = models.CharField(max_length=100, verbose_name="Шаг")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = TutorialStepPassQuerySet.as_manager()

    class Meta:
        verbose_name = "Шаг руководства"
        verbose_name_plural = "Шаги руководства"

    def __str__(self):
        return f"{self.user.account.get_short_name()}: {self.view}/{self.step}"
