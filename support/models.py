from django.db import models

from contest.abstract import CRUDEntry

"""==================================================== Question ===================================================="""


class Question(CRUDEntry):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(blank=True, verbose_name="Ответ")

    is_published = models.BooleanField(default=False, verbose_name="Опубликован?")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return "%s" % self.question


"""===================================================== Report ====================================================="""


class Report(CRUDEntry):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(blank=True, verbose_name="Сообщение")
    page_url = models.URLField(verbose_name="Откуда отправлено")

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Багрепорт"
        verbose_name_plural = "Багрепорты"

    def __str__(self):
        return self.title
