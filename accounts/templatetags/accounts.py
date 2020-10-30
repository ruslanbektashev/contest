from django import template
from django.contrib.contenttypes.models import ContentType

from accounts.models import Account
from accounts.views import comments_read

register = template.Library()


@register.simple_tag()
def get_unread_comments_number(comments_number, account_id, object_model, object_id):
    account = Account.objects.get(user_id=account_id)
    read_comments_number = account.comments_read.filter(
        object_type=ContentType.objects.get(app_label='contests', model=object_model),
        object_id=object_id
    ).count()
    return comments_number - read_comments_number


@register.simple_tag()
def mark_comments_as_read(request, account_id, object_model, object_id):
    return comments_read(request, account_id, object_model, object_id)
