from django import template
from django.contrib.contenttypes.models import ContentType
from accounts.models import Activity

register = template.Library()


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj) if hasattr(obj, 'comment_set') else 0
