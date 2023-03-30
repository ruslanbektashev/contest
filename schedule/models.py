import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import date
from django.utils import timezone

from accounts.models import Notification
from contest.abstract import CRUDEntry
from schedule.templatetags.events import iso_to_gregorian


def current_week_date_from(format_string='Y-m-d', next_week: bool = False):
    iso_today = timezone.now().isocalendar()
    week = (iso_today[1] + next_week) if (iso_today[1] + next_week) <= 52 else 1
    year = iso_today[0] if (iso_today[1] + next_week) <= 52 else iso_today[0] + 1
    date_from = iso_to_gregorian(year, week, 1)
    return "{}".format(date(date_from, format_string))


def current_week_date_to(format_string='Y-m-d', next_week: bool = False):
    iso_today = timezone.now().isocalendar()
    week = (iso_today[1] + next_week) if (iso_today[1] + next_week) <= 52 else 1
    year = iso_today[0] if (iso_today[1] + next_week) <= 52 else iso_today[0] + 1
    date_to = iso_to_gregorian(year, week, 7)
    return "{}".format(date(date_to, format_string))


class ScheduleQuerySet(models.QuerySet):
    def actual(self):
        return self.filter(date_from__range=[timezone.now().date() - timedelta(days=6),
                                             timezone.now().date() + timedelta(days=7)])


class Schedule(CRUDEntry):
    date_from = models.DateField(default=current_week_date_from, verbose_name="Начало интервала")
    date_to = models.DateField(default=current_week_date_to, verbose_name="Конец интервала")

    objects = ScheduleQuerySet.as_manager()

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
        return today < self.date_from <= today + timedelta(days=7)

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created:
            # TODO: notify related users
            # Notification.objects.notify()
            pass

    def __str__(self):
        return f"{date(self.date_from, 'd E Y')} - {date(self.date_to, 'd E Y')}"


def schedule_attachment_file_path(instance, filename):
    return "attachments/{app_label}/{model}/{id}/{filename}".format(app_label=instance.schedule._meta.app_label.lower(),
                                                                    model=instance.schedule._meta.object_name.lower(),
                                                                    id=instance.schedule.id,
                                                                    filename=filename)


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
