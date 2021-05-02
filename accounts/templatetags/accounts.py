from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template.defaultfilters import date
from django.utils import timezone

from accounts.models import Activity

register = template.Library()


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj) if hasattr(obj, 'comment_set') else 0


@register.simple_tag()
def unread_activities_count(user):
    return Activity.objects.filter(recipient=user, is_read=False).count()


@register.filter()
def naturaltime_if_lt_week_ago(value, arg=None):
    timediff = timezone.now() - value
    if timediff.days < 7:
        return naturaltime(value)
    else:
        return date(value, arg)


@register.simple_tag()
def subscription_id_for_course_id(user, course_id):
    return user.subscription_set.get(object_type=ContentType.objects.get(model='course'), object_id=course_id).id