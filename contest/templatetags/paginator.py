from django import template

register = template.Library()


@register.inclusion_tag('paginator.html', takes_context=True)
def render_page_nav(context):
    if context['page_obj'].number < 3:
        left_page = 0
    else:
        left_page = context['page_obj'].number - 3
    context['page_range'] = context['paginator'].page_range[left_page:context['page_obj'].number + 2]
    return context


