from django import template
from django.contrib.contenttypes.models import ContentType

from accounts.forms import CommentForm

register = template.Library()


@register.simple_tag()
def get_comment_query_string(page):
    page = str(page)
    query_string = ''
    if page != '1':
        query_string = '?page=' + page
    return query_string


@register.inclusion_tag('accounts/comment/comment_form.html')
def render_comment_form(obj, parent=None, form=None):
    if form is None:
        form = CommentForm()
    if obj:
        form.initial['object_type'] = ContentType.objects.get_for_model(obj)
        form.initial['object_id'] = obj.id
    if parent:
        form.initial['parent_id'] = parent.id
    context = {
        'form': form
    }
    return context


@register.inclusion_tag('accounts/comment/comment_list.html', takes_context=True)
def render_comments(context, obj, comments):
    context['obj'] = obj
    context['comments'] = comments
    return context


@register.filter
def model_name(instance):
    return instance._meta.model_name
