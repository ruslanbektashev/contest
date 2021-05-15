import re

from django import template
from django.apps import apps

register = template.Library()
Assignment = apps.get_model('contests', 'Assignment')

STATE_COLORS = {
    'OK': 'success',
    'TF': 'warning',
    'TR': 'warning',
    'WA': 'warning',
    'NA': 'warning',
    'TL': 'danger',
    'ML': 'danger',
    'CL': 'danger',
    'FE': 'danger',
    'SF': 'danger',
    'RE': 'danger',
    'CE': 'danger',
    'UE': 'danger',
    'PE': 'danger',
    'EX': 'danger',
    'UN': 'default',
    '5':  'success',
    5:    'success',
    '4':  'success',
    4:    'success',
    '3':  'warning',
    3:    'warning',
    '2':  'danger',
    2:    'danger',
    '1':  'danger',
    1:    'danger',
    '0':  'default',
    0:    'default'
}


@register.filter
def remove_pwd(string):
    return re.sub(r'/?[\w\-./]+/', '', string)


@register.filter
def colorize(value):
    return STATE_COLORS.get(value, 'info')


@register.filter
def colorize_solved_flag(value):
    return 'success' if value else 'danger'


@register.filter
def colorize_progress(value):
    if value >= 80:
        return 'success'
    elif value >= 60:
        return 'warning'
    elif value >= 40:
        return 'danger'
    else:
        return 'default'


@register.filter
def colorize_submission_count(submission_count, submission_limit=Assignment.DEFAULT_SUBMISSION_LIMIT):
    if submission_count == 0:
        return 'default'
    elif submission_count <= submission_limit / 2:
        return 'success'
    elif submission_count <= submission_limit:
        return 'warning'
    else:
        return 'danger'


@register.filter
def colorize_activity_count(value):
    return 'success' if value else 'default'


@register.simple_tag()
def account_course_score(account, course_id):
    return account.course_score(course_id=course_id)


@register.simple_tag()
def submissions_count(submissions, problem):
    return submissions.filter(problem=problem).count()


@register.simple_tag()
def solved(submissions, problem):
    return submissions.filter(problem=problem, status='OK').exists()


@register.simple_tag()
def get_problem_icon(problem):
    if problem.type == 'Text':
        return "fa-keyboard-o"
    elif problem.type == 'Files':
        return "fa-file-text-o"
    elif problem.type == 'Options':
        return "fa-check-square-o"
    elif problem.type == 'Program':
        return "fa-file-code-o"
    elif problem.type == 'Test':
        return "fa-folder-o"
    else:
        return "fa-ban"


@register.simple_tag()
def get_problem_subproblems(problem):
    subproblem_numbers = list(map(lambda x: "#" + str(x), problem.sub_problems.values_list('number', flat=True)))
    return ", ".join(subproblem_numbers)


@register.simple_tag()
def get_submission_style(submission):
    if submission.status == 'UN':
        return 'info'
    return colorize(submission.status)


@register.simple_tag()
def get_assignment_style(assignment):
    if assignment.latest_submission_status == 'UN' and assignment.latest_submission_date_created > assignment.date_updated:
        return 'info'
    return colorize(assignment.score)


@register.inclusion_tag('contests/assignment/assignment_user_table.html', takes_context=True)
def render_assignment_user_table(context, assignments, credits):
    for credit in credits:
        for assignment in assignments:
            if assignment.problem.contest.course_id == credit.course_id:
                assignment.credit = credit
    context['assignments'] = assignments
    return context


@register.inclusion_tag('contests/assignment/assignment_course_table.html')
def render_assignment_course_table(course, students, assignments, debts=False):
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
        'table': table,
        'debts': debts
    }
    return context


@register.inclusion_tag('contests/execution/execution_list.html', takes_context=True)
def render_execution_list(context, executions):
    context['executions'] = executions
    return context


@register.inclusion_tag('contests/attachment/attachment_list.html', takes_context=True)
def render_attachment_list(context, obj):
    context['attachments'] = obj.attachment_set.all()
    context['obj'] = obj
    context['path_name'] = 'contests:{}-attachment'.format(obj.__class__.__name__.lower())
    return context
