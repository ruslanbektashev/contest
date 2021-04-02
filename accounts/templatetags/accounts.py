from django import template
from django.contrib.contenttypes.models import ContentType
from accounts.models import Activity

register = template.Library()


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj) if hasattr(obj, 'comment_set') else 0


@register.simple_tag()
def mark_notification_as_read(account, obj):
    Activity.objects.filter(recipient=account.user, object_type=ContentType.objects.get_for_model(obj), object_id=obj.id).mark_as_read()
