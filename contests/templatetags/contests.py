import re

from django import template
from django.apps import apps
from django.conf import settings

register = template.Library()
Assignment = apps.get_model('contests', 'Assignment')

STATE_COLORS = {
    'OK': 'success',
    'PS': 'primary',
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
    'EV': 'info',
    'UN': 'default',
    '5':  'success',
    5:    'success',
    '4':  'primary',
    4:    'primary',
    '3':  'warning',
    3:    'warning',
    '2':  'danger',
    2:    'danger',
    '1':  'danger',
    1:    'danger',
    '0':  'default',
    0:    'default'
}


COURSE_DIFFICULTY_CHOICES = {
    0: 'Нет сведений',
    1: 'Легкий',
    2: 'Средний',
    3: 'Сложный',
}


@register.filter()
def remove_pwd(string):
    return re.sub(r'/?[\w\-./]+/', '', string)


@register.filter()
def colorize(value):
    return STATE_COLORS.get(value, 'info')


@register.filter()
def colorize_solved_flag(value):
    return 'success' if value else 'danger'


@register.filter()
def colorize_progress(value):
    if value >= 80:
        return 'success'
    elif value >= 60:
        return 'warning'
    elif value >= 40:
        return 'danger'
    else:
        return 'default'


@register.filter()
def colorize_submission_count(submission_count, submission_limit=Assignment.DEFAULT_SUBMISSION_LIMIT):
    if submission_count == 0:
        return 'default'
    elif submission_count <= submission_limit / 2:
        return 'success'
    elif submission_count <= submission_limit:
        return 'warning'
    else:
        return 'danger'


@register.filter()
def colorize_activity_count(value):
    return 'success' if value else 'default'


@register.filter()
def colorize_course_difficulty(value):
    if value == 1:
        return 'success'
    elif value == 2:
        return 'warning'
    elif value == 3:
        return 'danger'
    else:
        return 'default'


@register.filter()
def colorize_course_avg_score(value):
    if value >= 4.5:
        return 'success'
    elif value >= 3.5:
        return 'warning'
    elif value >= 2:
        return 'danger'
    else:
        return 'default'


@register.filter()
def course_difficulty(value):
    return COURSE_DIFFICULTY_CHOICES.get(value, 'Нет сведений')


@register.filter()
def course_filtered(request, course):
    return request.user.filter_set.filter(course=course).exists()


@register.filter()
def get_latest_submissions(course, request):
    latest_submissions = course.get_latest_submissions()
    if not request.user.account.faculty.is_interfaculty:
        latest_submissions = latest_submissions.filter(owner__account__faculty=request.user.account.faculty)
    return latest_submissions


@register.simple_tag()
def submissions_count(submissions, problem):
    return submissions.filter(problem=problem).count()


@register.simple_tag()
def solved(submissions, problem):
    return submissions.filter(problem=problem, status='OK').exists()


@register.simple_tag()
def get_problem_icon(problem):
    if problem.type == 'Text':
        return "fa-regular fa-keyboard"
    elif problem.type == 'Files':
        return "fa-regular fa-file"
    elif problem.type == 'Options':
        return "fa-regular fa-square-check"
    elif problem.type == 'Program':
        return "fa-regular fa-file-code"
    elif problem.type == 'Verbal':
        return "fa-regular fa-file-audio"
    elif problem.type == 'Test':
        return "fa-regular fa-folder"
    else:
        return "fa-regular fa-ban"


@register.simple_tag()
def get_problem_subproblems(problem):
    subproblem_numbers = list(map(lambda x: "#" + str(x), problem.sub_problems.values_list('number', flat=True)))
    return ", ".join(subproblem_numbers)


@register.filter()
def is_hidden_from_user(obj, request):
    return request.user.account.is_student and obj.hidden_from_students


@register.filter()
def is_visible_to_user(obj, request):
    return not request.user.account.is_student or obj.visible_to(request.user)


@register.filter()
def get_submission_status(submission, request):
    if submission.status != 'UN' and is_hidden_from_user(submission, request):
        return 'EV'
    return submission.status


@register.filter()
def get_submission_status_display(submission, request):
    if submission.status != 'UN' and is_hidden_from_user(submission, request):
        return "Посылка проверяется"
    return submission.get_status_display()


@register.filter()
def get_submission_score(submission, request):
    if submission.score != 0 and is_hidden_from_user(submission, request):
        return 0
    return submission.score


@register.filter()
def get_submission_score_percentage(submission, request):
    return get_submission_score(submission, request) * 100 // submission.problem.score_max


@register.filter()
def get_submission_style(submission, request):
    status = get_submission_status(submission, request)
    if status == 'UN':
        return 'default'
    return colorize(status)


@register.filter()
def get_assignment_score(assignment, request):
    if assignment.score != 0 and is_hidden_from_user(assignment, request):
        return 0
    return assignment.score


@register.filter()
def get_assignment_style(assignment):
    if assignment.latest_submission_status == 'UN' and assignment.latest_submission_date_created > assignment.date_updated:
        return 'info'
    return colorize(assignment.score)


@register.inclusion_tag('contests/attendance/attendance_course_table.html', takes_context=True)
def render_attendance_course_table(context, students, attendance):
    table = []
    days = attendance.dates('date_from', 'day', order='ASC')
    attendance_num, days_num = len(attendance), len(days)
    i = 0
    for student in students:
        row = {'student': student, 'columns': [{'day': day, 'attendance': [], 'sum': 0} for day in days]}
        j = 0
        while i < attendance_num and attendance[i].user_id == student.user_id:
            while j < days_num and days[j] != attendance[i].date_from.date():
                j += 1
            if days[j] == attendance[i].date_from.date():
                row['columns'][j]['attendance'].append(attendance[i])
                if attendance[i].flag:
                    row['columns'][j]['sum'] += 1
                i += 1
        table.append(row)
    context.update(dict(days=days, table=table))
    return context


@register.inclusion_tag('contests/assignment/assignment_user_table.html', takes_context=True)
def render_assignment_user_table(context, assignments, credits):
    for credit in credits:
        for assignment in assignments:
            if assignment.contest.course_id == credit.course_id:
                assignment.attached_credit = credit
    context['assignments'] = assignments
    return context


@register.inclusion_tag('contests/assignment/assignment_course_table.html', takes_context=True)
def render_assignment_course_table(context, course, students, assignments):
    table = []
    contests = course.contest_set.all()
    assignments_num, contests_num = len(assignments), len(contests)
    i = 0
    for student in students:
        row = {'student': student, 'columns': [{'contest': contest, 'assignments': []} for contest in contests]}
        j = 0
        while i < assignments_num and assignments[i].user_id == student.user_id:
            while j < contests_num and contests[j].id != assignments[i].problem.contest_id:
                j += 1
            if contests[j].id == assignments[i].problem.contest_id:
                row['columns'][j]['assignments'].append(assignments[i])
                i += 1
        table.append(row)
    context.update(dict(contests=contests, table=table))
    return context


@register.inclusion_tag('contests/attachment/attachment_list.html', takes_context=True)
def render_attachment_list(context, obj, course):
    context['attachments'] = obj.attachment_set.all()
    context['obj'] = obj
    context['course'] = course
    context['detail_view_name'] = 'contests:{}-attachment'.format(obj.__class__.__name__.lower())
    context['update_view_name'] = 'contests:{}-update'.format(obj.__class__.__name__.lower())
    context['contest_domain'] = settings.CONTEST_DOMAIN
    return context
