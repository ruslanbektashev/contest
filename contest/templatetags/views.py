from django import template

register = template.Library()


@register.inclusion_tag('list.html')
def render_list(lst, legend=None):
    context = {
        'lst': lst,
        'legend': legend or ""
    }
    return context


@register.inclusion_tag('media_list.html')
def render_media_list(lst, legend=None):
    context = {
        'lst': lst,
        'legend': legend or ""
    }
    return context
