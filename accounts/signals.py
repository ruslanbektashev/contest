from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Activity, Comment
from support.models import Report


@receiver(post_save, sender=Report)
def receive_report_signal(sender, instance, **kwargs):
    Activity.objects.notify_group(group_name='Преподаватель', subject=instance.owner, action="отправил багрепорт",
                                  object=instance)


@receiver(post_save, sender=Comment)
def receive_comment_signal(sender, instance, created, **kwargs):
    if created:
        for subscriber in instance.object.subscribers.all():
            Activity.objects.notify_user(subscriber.username, subject=instance.author, action='оставил комментарий', object=instance)
