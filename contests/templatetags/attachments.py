from django import template
from django.core.exceptions import ImproperlyConfigured

register = template.Library()


@register.inclusion_tag('contests/attachment/attachment_list.html', takes_context=True)
def render_attachment_list(context, entry, legend=None):
    try:
        context['attachments'] = entry.attachment_set.all()
    except AttributeError:
        raise ImproperlyConfigured("GenericRelation manager should be declared in this model in order to retrieve "
                                   "attachments")
    context['legend'] = legend or "Файлы"
    return context
