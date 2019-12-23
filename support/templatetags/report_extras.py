from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_prev_url(url):
    return reverse('support:report-create') + "?from=" + url
