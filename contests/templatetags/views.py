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


@register.inclusion_tag('progress.html')
def render_progress(value, title):
    return {'progress': value, 'title': title}


@register.inclusion_tag('progress.html')
def render_assignment_progress(assignments, title):
    return {'progress': assignments.progress(), 'title': title}


@register.inclusion_tag('progress.html')
def render_submission_progress(submission, title):
    score = round(submission.score * 100 / submission.problem.score_max)
    return {'progress': score, 'title': title}


@register.filter()
def has_owner_permission(request, course):
    return course.owner_id == request.user.id


@register.filter()
def has_leader_permission(request, course):
    return course.leaders.filter(id=request.user.id).exists() or course.owner_id == request.user.id


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
    if _GET:
        return '?' + '&'.join(['{}={}'.format(key, value) for key, value in _GET.items()])  # _GET.urlencode()
    else:
        return ''


@register.simple_tag()
def get_full_path_with_updated_query_string(request, **kwargs):
    return request.path + get_updated_query_string(request, **kwargs)


@register.filter()
def get_query_string(request):
    return '?' + '&'.join(['{}={}'.format(key, value) for key, value in request.GET.items()])


@register.inclusion_tag('page_nav.html', takes_context=True)
def render_page_nav(context):
    if context['page_obj'].number < 3:
        left_page = 0
    else:
        left_page = context['page_obj'].number - 3
    context['page_range'] = context['paginator'].page_range[left_page:context['page_obj'].number + 2]
    return context
