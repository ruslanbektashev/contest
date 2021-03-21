from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Entry(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        abstract = True


class CDEntry(Entry):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta(Entry.Meta):
        abstract = True
        ordering = ('date_created',)


class CRDEntry(CDEntry):
    class Meta(CDEntry.Meta):
        abstract = True

    def get_absolute_url(self):
        return reverse('{app_label}:{model}-detail'.format(app_label=self._meta.app_label.lower(),
                                                           model=self._meta.object_name.lower()),
                       kwargs={'pk': self.pk})


class CRUDEntry(CRDEntry):
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta(CRDEntry.Meta):
        abstract = True
