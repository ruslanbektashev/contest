from django import template

from support.models import TutorialStepPass

register = template.Library()


@register.simple_tag()
def tutorial_step_view(request):
    return "{}:{}".format(request.resolver_match.app_name, request.resolver_match.url_name)


@register.filter()
def have_passed_step(request, step):
    view = tutorial_step_view(request)
    return TutorialStepPass.objects.is_step_passed(request.user, view, step)
