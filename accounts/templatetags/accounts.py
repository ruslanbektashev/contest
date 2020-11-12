from django import template

from accounts.models import Account

register = template.Library()


@register.simple_tag()
def mark_comments_as_read(account, obj):
    return account.mark_comments_as_read(obj)


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj)
