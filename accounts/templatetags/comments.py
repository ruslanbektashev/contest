from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured

from accounts.forms import CommentForm

register = template.Library()


@register.inclusion_tag('accounts/comment/comment_form.html')
def render_comment_form(entry, parent=None):
    form = CommentForm(initial={
        'object_type': ContentType.objects.get_for_model(entry),
        'object_id': entry.id
    })
    if parent:
        form.initial['parent_id'] = parent.id
    context = {
        'form': form
    }
    return context


@register.inclusion_tag('accounts/comment/comment_list.html', takes_context=True)
def render_comment_list(context, entry):
    try:
        context['comments'] = entry.comment_set.actual()
    except AttributeError:
        raise ImproperlyConfigured("GenericRelation manager should be declared in this model in order to retrieve "
                                   "comments")
    return context


@register.inclusion_tag('accounts/comment/comments.html', takes_context=True)
def render_comments(context, entry):
    context['entry'] = entry
    return context
