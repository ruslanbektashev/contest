from django import template

register = template.Library()


@register.simple_tag()
def unread_comments_count(account, obj):
    return account.unread_comments_count(obj)
