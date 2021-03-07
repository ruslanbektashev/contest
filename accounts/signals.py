from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Activity, Comment
from support.models import Report
from contests.models import Submission


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
    users = course.subscription_set.exclude(user=instance.author).values_list('user_id', flat=True)
    if instance.author_id != instance.object.owner_id:
        user_set = set(users)
        user_set.add(instance.object.owner_id)
        users = list(user_set)
    action = "оставил комментарий" if created else "изменил комментарий"
    Activity.objects.notify_users(users, subject=instance.author, action=action, object=instance,
                                  reference=instance.object)


@receiver(post_save, sender=Submission)
def receive_submission_signal(sender, instance, created, **kwargs):
    if created:
        course = instance.problem.contest.course
        users = course.subscription_set.values_list('user_id', flat=True)
        action = "отправил посылку"
        Activity.objects.notify_users(users, subject=instance.owner, action=action, object=instance)
