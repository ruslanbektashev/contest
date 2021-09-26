from django import template

from support.models import TutorialStepPass

register = template.Library()


@register.filter
def have_passed_step(user, step_key):
    # temporary solution
    if not user.is_superuser:
        if user.account.is_student:
            return True
        if user.date_joined.year < 2021 and user.id != 52:
            return True
    view, step = step_key.split('/')
    return TutorialStepPass.objects.filter(user=user, view=view, step=step).exists()
