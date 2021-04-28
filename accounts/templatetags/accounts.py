from accounts.models import Activity
from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj) if hasattr(obj, 'comment_set') else 0


@register.simple_tag()
def unread_activities_count(user):
    return Activity.objects.filter(recipient=user, is_read=False).count()


@register.simple_tag()
def subscription_id_for_course_id(user, course_id):
    return user.subscription_set.get(object_type=ContentType.objects.get(model='course'), object_id=course_id).id