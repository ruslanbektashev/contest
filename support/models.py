from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.urls import reverse

from contest.abstract import CRUDEntry

"""==================================================== Account ====================================================="""


class FAQ(CRUDEntry):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(blank=True, verbose_name="Ответ")

    is_published = models.BooleanField(default=False, verbose_name="Опубликовано?")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return "%s" % self.question


"""===================================================== Report ====================================================="""


class Report(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(blank=True, verbose_name="Отчёт")
    sending_time = models.DateTimeField(default=timezone.now, verbose_name="Время отправки")
    page_url = models.URLField(verbose_name="Откуда отправлено")
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Отправитель")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('support:report-detail', kwargs={'pk': self.pk})
