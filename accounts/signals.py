from django.dispatch import Signal
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ActivityManager
from support.models import Report

# activity_manager = ActivityManager()
#
#
# @receiver(post_save, sender=Report)
# def receive_report_signal(sender, instance, **kwargs):
#     activity_manager.notify_group(sender=instance.sender, group_name='staff', action="отправил багрепорт",
#                                   object=instance)
