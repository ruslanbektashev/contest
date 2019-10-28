from django import template

from tools.sandbox import secure

register = template.Library()

STATE_COLORS = {
    'OK': 'success',
    'TF': 'warning',
    'WA': 'warning',
    'NA': 'warning',
    'TL': 'danger',
    'ML': 'danger',
    'FE': 'danger',
    'SF': 'danger',
    'RE': 'danger',
    'CE': 'danger',
    'UE': 'danger',
    'PE': 'danger',
    'UN': 'default',
    '5': 'success',
    '4': 'success',
    '3': 'warning',
    '2': 'danger',
    '1': 'default',
    '0': 'default'
}


@register.filter
def remove_pwd(string):
    return secure(string)


@register.filter
def colorize(value):
    return STATE_COLORS[value]


@register.simple_tag
def get_label(value):
    try:
        score = int(value)
    except ValueError:
        if value == 'UN':
            return 'label-default'
        elif value == 'EX':
            return 'label-primary'
        elif value in ('GO', 'OK'):
            return 'label-success'
        elif value in ('SA', 'WA', 'TF', 'NA'):
            return 'label-warning'
        else:
            return 'label-danger'
    else:
        if score < 2 or score > 5:
            return 'label-default'
        elif score == 2:
            return 'label-danger'
        elif score == 3:
            return 'label-warning'
        elif score == 4:
            return 'label-success'
        elif score == 5:
            return 'label-primary'


@register.inclusion_tag('contests/submission/submission_table.html', takes_context=True)
def render_submission_table(context):
    return context


@register.inclusion_tag('contests/assignment/assignment_user_table.html', takes_context=True)
def render_assignment_user_table(context, assignments, credits):
    for credit in credits:
        for assignment in assignments:
            if assignment.problem.contest.course_id == credit.course_id:
                assignment.credit = credit
    context['assignments'] = assignments
    return context


@register.inclusion_tag('contests/assignment/assignment_course_table.html')
def render_assignment_course_table(course, students, assignments):
    table = []
    contests = course.contest_set.all()
    nassignments, ncontests = len(assignments), len(contests)
    i = 0
    for student in students:
        row = {'student': student, 'columns': [{'contest': contest, 'assignments': []} for contest in contests]}
        j = 0
        while i < nassignments and assignments[i].user_id == student.user_id:
            while j < ncontests and contests[j].id != assignments[i].problem.contest_id:
                j += 1
            if contests[j].id == assignments[i].problem.contest_id:
                row['columns'][j]['assignments'].append(assignments[i])
                i += 1
        table.append(row)
    context = {
        'course': course,
        'contests': contests,
        'table': table
    }
    return context


@register.inclusion_tag('contests/assignment/assignment_progress.html')
def render_assignment_progress(assignments):
    return {'progress': assignments.progress()}


@register.inclusion_tag('contests/execution/execution_list.html', takes_context=True)
def render_execution_list(context, executions):
    context['executions'] = executions
    return context
