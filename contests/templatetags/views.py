from django import template
from django.shortcuts import resolve_url

register = template.Library()


@register.inclusion_tag('breadcrumb.html')
def breadcrumb(title, *args, query_string=None, **kwargs):
    context = {
        'title': title,
        'url': resolve_url(*args, **kwargs) if args else None
    }
    if isinstance(query_string, str):
        context['url'] += query_string
    return context


@register.filter()
def has_owner_permission(request, course):
    return course.owner_id == request.user.id


@register.filter()
def has_leader_permission(request, course):
    return course.leaders.filter(id=request.user.id).exists() or course.owner_id == request.user.id


@register.filter()
def has_author_permission(request, course):
    return course.author.id == request.user.id


@register.filter()
def has_student_permission(request, user):
    return user.id == request.user.id


@register.filter()
def exists(file):
    return file.storage.exists(file.path)


@register.simple_tag()
def get_updated_query_string(request, **kwargs):
    _GET = request.GET.copy()
    _GET.update(kwargs)
    query_string = '&'.join(['{}={}'.format(key, value) for key, value in _GET.items()])  # _GET.urlencode()
    return '?' + query_string if query_string else ''


@register.simple_tag()
def get_full_path_with_updated_query_string(request, **kwargs):
    return request.path + get_updated_query_string(request, **kwargs)


@register.filter()
def get_query_string(request):
    query_string = '&'.join(['{}={}'.format(key, value) for key, value in request.GET.items()])
    return '?' + query_string if query_string else ''


@register.inclusion_tag('page_nav.html', takes_context=True)
def render_page_nav(context):
    page_obj = context['page_obj']
    if page_obj.number < 3:
        left_page = 0
    else:
        left_page = page_obj.number - 3
    context['page_range'] = page_obj.paginator.page_range[left_page:page_obj.number + 2]
    return context
