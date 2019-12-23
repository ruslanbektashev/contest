from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Activity
from support.models import Report


@receiver(post_save, sender=Report)
def receive_report_signal(sender, instance, **kwargs):
    Activity.objects.notify_group(sender=instance.sender, group_name='Преподаватель', action="отправил багрепорт",
                                  object=instance)
