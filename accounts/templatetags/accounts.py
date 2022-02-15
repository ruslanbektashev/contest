from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.defaultfilters import date
from django.utils import timezone

from accounts.models import Notification

register = template.Library()


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj) if hasattr(obj, 'comment_set') else 0


@register.simple_tag()
def unread_notifications_count(user):
    return Notification.objects.filter(recipient=user, is_read=False).count()


@register.filter()
def naturaltime_if_lt_week_ago(value, arg=None):
    timediff = timezone.now() - value
    if timediff.days < 7:
        return naturaltime(value)
    else:
        return date(value, arg)


@register.simple_tag()
def course_contests(course, contests):
    return contests.filter(course=course.id)
