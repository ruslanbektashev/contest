from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Activity, Comment, Account
from support.models import Report


@receiver(post_save, sender=Report)
def receive_report_signal(sender, instance, **kwargs):
    Activity.objects.notify_group(group_name='Преподаватель', subject=instance.owner, action="отправил багрепорт",
                                  object=instance)


@receiver(post_save, sender=Comment)
def receive_comment_signal(sender, instance, created, **kwargs):
    def get_course_for_comment(comment):
        model = comment.object_type.model
        if model == 'course':
            return comment.object
        elif model == 'contest':
            return comment.object.course
        elif model == 'problem':
            return comment.object.contest.course
        elif model == 'assignment' or 'submission':
            return comment.object.problem.contest.course

    course = get_course_for_comment(instance)

    if created:
        for account in Account.objects.all():
            if course in account.subscriptions.all() and instance.author != account.user:
                Activity.objects.notify_user(account.username, subject=instance.author, action='оставил комментарий',
                                             object=instance)
