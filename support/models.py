from django.db import models

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


class Report(CRUDEntry):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(blank=True, verbose_name="Отчет")
    page_url = models.URLField(verbose_name="Откуда отправлено")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Отчет об ошибке"
        verbose_name_plural = "Отчеты об ошибках"

    def __str__(self):
        return self.title
