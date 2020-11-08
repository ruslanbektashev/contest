from django import template

from accounts.models import Account

register = template.Library()


@register.simple_tag()
def mark_comments_as_read(account_id, obj):
    try:
        account = Account.objects.get(user_id=account_id)
    except Account.DoesNotExist:
        return

    return account.mark_comments_as_read(obj)
