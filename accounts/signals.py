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

    if created:
        course = get_course_for_comment(instance)
        Activity.objects.notify_users(
            course.subscription_set.exclude(account=instance.author.account).values_list('account', flat=True),
            subject=instance.author,
            action='оставил комментарий',
            object=instance
        )
