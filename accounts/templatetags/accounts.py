from django import template

from accounts.views import mark_comments_as_read

register = template.Library()


@register.simple_tag()
def comments_read(request, account_id, object_model, object_id):
    return mark_comments_as_read(request, account_id, object_model, object_id)
