from django import template

from accounts.views import mark_comments_as_read as mark_comments_as_read_view

register = template.Library()


@register.simple_tag()
def mark_comments_as_read(request, account_id, object):
    return mark_comments_as_read_view(request, account_id, object)
