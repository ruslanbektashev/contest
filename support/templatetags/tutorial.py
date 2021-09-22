from django import template

from support.models import TutorialStepPass

register = template.Library()


@register.filter
def have_passed_step(user, step_key):
    # temporary solution
    if user.account.faculty_id == 1 and user.id != 52 and not user.is_superuser:
        return True
    view, step = step_key.split('/')
    return TutorialStepPass.objects.filter(user=user, view=view, step=step).exists()
