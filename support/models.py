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
