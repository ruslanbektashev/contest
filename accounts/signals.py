from django.dispatch import Signal
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ActivityManager
from support.models import Report
from .models import Activity


@receiver(post_save, sender=Report)
def receive_report_signal(sender, instance, **kwargs):
    Activity.objects.notify_group(sender=instance.sender, group_name='Преподаватели', action="отправил багрепорт",
                                  object=instance)
