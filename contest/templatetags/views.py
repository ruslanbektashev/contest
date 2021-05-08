from django import template
from django.shortcuts import resolve_url

register = template.Library()


@register.inclusion_tag('breadcrumb.html')
def breadcrumb(title, *args, **kwargs):
    context = {
        'title': title,
        'url': resolve_url(*args, **kwargs) if args else None
    }
    return context


@register.simple_tag()
def get_updated_query_string(request, **kwargs):
    _GET = request.GET.copy()
    _GET.update(kwargs)
    return '?' + '&'.join(['{}={}'.format(key, value) for key, value in _GET.items()])


@register.simple_tag()
def get_full_path_with_updated_query_string(request, **kwargs):
    _GET = request.GET.copy()
    _GET.update(kwargs)
    return request.path + '?' + '&'.join(['{}={}'.format(key, value) for key, value in _GET.items()])


@register.inclusion_tag('page_nav.html', takes_context=True)
def render_page_nav(context):
    if context['page_obj'].number < 3:
        left_page = 0
    else:
        left_page = context['page_obj'].number - 3
    context['page_range'] = context['paginator'].page_range[left_page:context['page_obj'].number + 2]
    return context
