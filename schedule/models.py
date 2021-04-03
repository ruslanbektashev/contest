import os

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import date
from django.utils import timezone

from accounts.models import Activity
from contest.abstract import CRUDEntry
from contests.templatetags.events import iso_to_gregorian


def current_week_date_from(format_string='Y-m-d'):
    iso_today = timezone.now().isocalendar()
    date_from = iso_to_gregorian(iso_today[0], iso_today[1], 1)
    return "{}".format(date(date_from, format_string))


def current_week_date_to(format_string='Y-m-d'):
    iso_today = timezone.now().isocalendar()
    date_to = iso_to_gregorian(iso_today[0], iso_today[1], 7)
    return "{}".format(date(date_to, format_string))


class Schedule(CRUDEntry):
    date_from = models.DateField(default=current_week_date_from, verbose_name="Начало интервала")
    date_to = models.DateField(default=current_week_date_to, verbose_name="Конец интервала")

    class Meta(CRUDEntry.Meta):
        unique_together = ('date_from', 'date_to')
        ordering = ('-date_from', '-date_to', '-date_created')
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    def is_current(self):
        today = timezone.now().date()
        return self.date_from <= today <= self.date_to

    def is_upcoming(self):
        today = timezone.now().date()
        return today < self.date_from

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created:
            user_ids = User.objects.values_list('id', flat=True)
            Activity.objects.notify_users(user_ids, subject=self.owner, action="добавил расписание", object=self)

    def __str__(self):
        return "{} - {}".format(date(self.date_from, 'd E Y'), date(self.date_to, 'd E Y'))


def schedule_attachment_file_path(instance, filename):
    return "attachments/{app_label}/{model}/{id}/{filename}".format(
        app_label=instance.schedule._meta.app_label.lower(),
        model=instance.schedule._meta.object_name.lower(),
        id=instance.schedule.id,
        filename=filename
    )


class ScheduleAttachment(CRUDEntry):
    owner = None
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name="Расписание")
    name = models.CharField(max_length=100, verbose_name="Название")
    file = models.FileField(upload_to=schedule_attachment_file_path, verbose_name="Файл")

    def __str__(self):
        return self.name


@receiver(models.signals.post_delete, sender=ScheduleAttachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ deletes file from filesystem when corresponding `ScheduleAttachment` object is deleted. """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
