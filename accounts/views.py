import json

from markdown import markdown

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView, FormView, TemplateView

from accounts.forms import AccountPartialForm, AccountListForm, AccountSetForm, CommentForm, StaffForm, StudentForm
from accounts.models import Account, Comment, Faculty, Announcement, Notification
from accounts.templatetags.comments import get_comment_query_string
from contest.mixins import LoginRedirectMixin, OwnershipOrMixin, PaginatorMixin
from contest.templatetags.views import get_query_string, get_updated_query_string
from contests.models import Course, Problem, Submission
from support.models import Question, Report

"""==================================================== Account ====================================================="""


def nextmonth(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1


def get_study_years_list(account):
    today = datetime.today()
    current_year = today.year if today.month >= 9 else today.year - 1
    years = [(current_year - i, str(current_year - i) + '-' + str(current_year - i + 1) + ' учебный год') for i in range(current_year - account.admission_year + 1 or 1)]
    return years


def get_year_month_submissions_solutions_comments_count_list(user, year):
    Assignment = apps.get_model('contests', 'Assignment')
    academic_year_start_month = 9
    today = timezone.localdate()
    all_time = not year
    if all_time:
        year = user.account.admission_year
    day = datetime(year, academic_year_start_month, 1)
    submissions = user.submission_set.filter(date_created__year=day.year, date_created__month=day.month)
    problem_ids = submissions.values_list('problem', flat=True).distinct().order_by()
    problems_count = 0
    counted_problem_ids = []
    for problem_id in problem_ids:
        if problem_id not in counted_problem_ids and (submissions.filter(problem_id=problem_id, status='OK').exists() or Assignment.objects.filter(user=user, problem_id=problem_id, score__gte=3).exists()):
            problems_count += 1
            counted_problem_ids.append(problem_id)
    result = [(
        day.year,
        date(day, 'F'),
        submissions.count(),
        problems_count,
        Comment.objects.filter(author=user, date_created__year=day.year, date_created__month=day.month).count(),
    )]
    while (not all_time and (day.year != today.year and day.month != academic_year_start_month - 1 or day.year == today.year and day.month != today.month)) or (all_time and day < datetime(today.year, today.month, 1)):
        day = datetime(*nextmonth(year=day.year, month=day.month), 1)
        submissions = user.submission_set.filter(date_created__year=day.year, date_created__month=day.month)
        problem_ids = submissions.values_list('problem', flat=True).distinct().order_by()
        problems_count = 0
        for problem_id in problem_ids:
            if problem_id not in counted_problem_ids and (submissions.filter(problem_id=problem_id, status='OK').exists() or Assignment.objects.filter(user=user, problem_id=problem_id, score__gte=3).exists()):
                problems_count += 1
                counted_problem_ids.append(problem_id)
        result.append((
            day.year,
            date(day, 'F'),
            submissions.count(),
            problems_count,
            Comment.objects.filter(author=user, date_created__year=day.year, date_created__month=day.month).count(),
        ))
    return result


@csrf_exempt
def mark_comments_as_read(request):
    account = request.user.account
    try:
        data = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'status': 'bad_request'})
    unread_comments_ids = data.get('unread_comments_ids', None)
    if unread_comments_ids:
        unread_comments = Comment.objects.filter(id__in=unread_comments_ids).exclude(author=request.user)
        unread_comments = unread_comments.exclude(id__in=account.comments_read.values_list('id', flat=True))
        account.mark_comments_as_read(unread_comments)
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def mark_notifications_as_read(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'status': 'bad_request'})
    unread_notifications_ids = data.get('unread_notifications_ids', None)
    if unread_notifications_ids:
        unread_notifications = Notification.objects.filter(id__in=unread_notifications_ids, recipient=request.user)
        unread_notifications.mark_as_read()
    return JsonResponse({'status': 'ok'})


class AccountDetail(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account/account_detail.html'
    permission_required = 'accounts.view_account'

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.user_id == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.is_student:
            context['assignments'] = (self.object.user.assignment_set
                                      .select_related('problem', 'problem__contest', 'problem__contest__course')
                                      .order_by('-problem__contest__course', '-problem__contest', '-date_created'))
            context['credits'] = self.object.user.credit_set.select_related('course').order_by('course')
            context['comments_count'] = Comment.objects.filter(author=self.object.user).count()
            context['questions_count'] = Question.objects.filter(owner=self.object.user).count()
            context['reports_count'] = Report.objects.filter(owner=self.object.user).count()
            context['submissions_count'] = Submission.objects.filter(owner=self.object.user).count()
            context['problems_count'] = self.object.solved_problems_count
            years_list = get_study_years_list(self.object)
            years_list.append((0, 'Все время'))
            year = int(self.request.GET.get('year') or years_list[0][0])
            context['year_month_submissions_solutions_comments'] = get_year_month_submissions_solutions_comments_count_list(self.object.user, year)
            context['years'] = years_list
            context['year'] = year
        return context


class AccountCreateSet(LoginRedirectMixin, PermissionRequiredMixin, FormView):
    form_class = AccountSetForm
    template_name = 'accounts/account/account_set_form.html'
    permission_required = 'accounts.add_account'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            faculty_id = int(request.GET.get('faculty_id') or request.user.account.faculty_id)
            self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
            self.storage['level'] = int(request.GET.get('level') or 1)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.storage['faculty']
        kwargs['level'] = self.storage['level']
        return kwargs

    def form_valid(self, form):
        try:
            if form.cleaned_data['type'] == 1:
                _, self.request.session['credentials'] = Account.students.create_set(form.cleaned_data['faculty'],
                                                                                     form.cleaned_data['level'],
                                                                                     form.cleaned_data['admission_year'],
                                                                                     form.cleaned_data['names'])
            else:
                _, self.request.session['credentials'] = Account.staff.create_set(form.cleaned_data['faculty'],
                                                                                  form.cleaned_data['level'],
                                                                                  form.cleaned_data['type'],
                                                                                  form.cleaned_data['admission_year'],
                                                                                  form.cleaned_data['names'])
        except ValueError as e:
            form.add_error('names', str(e))
            return self.form_invalid(form)
        self.storage['faculty'] = form.cleaned_data['faculty']
        self.storage['level'] = form.cleaned_data['level']
        self.storage['type'] = form.cleaned_data['type']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty'] = self.storage['faculty']
        return context

    def get_success_url(self):
        return reverse('accounts:account-credentials') + get_updated_query_string(self.request,
                                                                                  faculty_id=self.storage['faculty'].id,
                                                                                  level=self.storage['level'],
                                                                                  type=self.storage['type'])


class AccountUpdate(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, UpdateView):
    model = Account
    template_name = 'accounts/account/account_form.html'
    permission_required = 'accounts.change_account'

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.user_id == self.request.user.id

    def get_form_class(self):
        if self.request.user.has_perm('accounts.change_account'):
            if self.object.type > 1:
                return StaffForm
            else:
                return StudentForm
        else:
            return AccountPartialForm


class AccountUpdateSet(LoginRedirectMixin, PermissionRequiredMixin, FormView):
    template_name = 'accounts/account/account_formset.html'
    permission_required = 'accounts.change_account'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            faculty_id = int(request.GET.get('faculty_id') or request.user.account.faculty_id)
            self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
            self.storage['level'] = int(request.GET.get('level') or 1)
            self.storage['type'] = int(request.GET.get('type') or 1)
            enrolled, graduated = request.GET.get('enrolled'), request.GET.get('graduated')
            self.storage['enrolled'] = True
            self.storage['graduated'] = False
            if enrolled is not None and enrolled == '0':
                self.storage['enrolled'] = False
            if graduated is not None and graduated == '1':
                self.storage['graduated'] = True
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.storage['type'] > 1:
            queryset = Account.staff.filter(type=self.storage['type'])
        else:
            queryset = Account.students.filter(enrolled=self.storage['enrolled'], graduated=self.storage['graduated'])
            if self.storage['level'] and self.storage['enrolled'] and not self.storage['graduated']:
                queryset = queryset.filter(level=self.storage['level'])
        queryset = queryset.filter(faculty=self.storage['faculty'])
        return queryset

    def get_form_class(self):
        if self.storage['type'] > 1:
            form = StaffForm
        else:
            form = StudentForm
        return modelformset_factory(Account, form=form, extra=0)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def form_valid(self, form):
        self.objects = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = context['form']
        context.update(self.storage)
        return context

    def get_success_url(self):
        return reverse('accounts:account-list') + get_query_string(self.request)


class AccountFormList(AccountUpdateSet):
    template_name = 'accounts/account/account_list.html'
    permission_required = 'accounts.change_account'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            action = request.POST.get('action')
            accounts = form.cleaned_data['accounts']
            if action == 'reset_password':
                self.request.session['credentials'] = accounts.reset_password()
                return HttpResponseRedirect(reverse('accounts:account-credentials') + get_query_string(request))
            elif self.storage['type'] == 1:
                if action == 'level_up':
                    accounts.level_up()
                elif action == 'level_down':
                    accounts.level_down()
                elif action == 'enroll':
                    accounts.enroll()
                elif action == 'expel':
                    accounts.expel()
                elif action == 'graduate':
                    accounts.graduate()
            else:
                form.add_error(None, "Недопустимое действие для данного типа пользователей.")
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_class(self):
        return AccountListForm

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        LEVEL_CHOICES = list(Account.LEVEL_CHOICES)
        LEVEL_CHOICES.insert(0, (0, "Все уровни"))
        context['level_choices'] = LEVEL_CHOICES
        context['faculty_choices'] = list((f.id, f.short_name) for f in Faculty.objects.all())
        return context

    def get_success_url(self):
        return self.request.get_full_path()


class AccountCredentials(LoginRedirectMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'accounts/account/account_credentials.html'
    permission_required = 'accounts.add_account'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.storage['credentials'] = self.request.session.pop('credentials', None)
            faculty_id = int(request.GET.get('faculty_id') or request.user.account.faculty_id)
            self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['credentials'] = self.storage.pop('credentials')
        context['faculty'] = self.storage['faculty']
        return context


class AccountCourseResults(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account/account_course_results.html'
    permission_required = 'accounts.view_account'

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.user_id == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = course = Course.objects.get(id=self.kwargs.get('course_id'))
        context['assignments'] = (self.object.user.assignment_set.filter(problem__contest__course=course)
                                  .select_related('problem', 'problem__contest')
                                  .order_by('problem__contest__course', 'problem__contest', 'date_created'))
        context['credit'] = self.object.user.credit_set.get(course=course)
        context['additional_submissions'] = (self.object.user.submission_set.filter(problem__contest__course=course,
                                                                                    assignment__isnull=True)
                                             .select_related('problem', 'problem__contest')
                                             .order_by('problem__contest', 'problem'))
        context['course_submissions_score'] = self.object.course_submissions_score(course)
        return context


class AccountAssignmentList(LoginRedirectMixin, PermissionRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account/account_assignment_list.html'
    permission_required = 'accounts.view_account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = (self.object.user.assignment_set
                                  .select_related('problem', 'problem__contest', 'problem__contest__course')
                                  .order_by('-problem__contest__course', '-problem__contest', '-date_created'))
        context['credits'] = self.object.user.credit_set.select_related('course').order_by('course')
        return context


class AccountProblemSubmissionList(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account/account_problem_submissions.html'
    permission_required = 'accounts.view_account'

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.user_id == self.request.user.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = Problem.objects.get(id=self.kwargs.get('problem_id'))
        context['submissions'] = (self.object.user.submission_set.filter(problem=context['problem'])
                                  .order_by('date_created'))
        return context


"""==================================================== Comment ====================================================="""


class CommentCreate(LoginRedirectMixin, PermissionRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'accounts/comment/comment_reply.html'
    permission_required = 'accounts.add_comment'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        try:
            self.storage['parent'] = Comment.objects.get(id=kwargs.pop('pk', 0))
        except Comment.DoesNotExist:
            self.storage['parent'] = None
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        if not form.instance.parent_id:
            messages.warning(self.request, "<br/>".join(form.errors['text']))
            return HttpResponseRedirect(form.instance.object.get_discussion_url())
        else:
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent'] = self.storage['parent']
        return context

    def get_success_url(self):
        return self.object.object.get_discussion_url() + '#comment_' + str(self.object.pk)


class CommentUpdate(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'accounts/comment/comment_update.html'
    permission_required = 'accounts.change_comment'

    def has_ownership(self):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        return self.object.author_id == self.request.user.id

    def get_success_url(self):
        page = self.request.GET.get('page', '1')
        return self.object.object.get_discussion_url() + get_comment_query_string(page) + '#comment_' + str(self.object.pk)


class CommentDelete(LoginRedirectMixin, PermissionRequiredMixin, DeleteView):
    model = Comment
    template_name = 'accounts/comment/comment_delete.html'
    permission_required = 'accounts.delete_comment'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['thread_length'] = self.object.soft_delete(commit=False)
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.soft_delete(delete_threads=request.user.has_perm(self.permission_required))
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        page = self.request.GET.get('page', '1')
        return self.object.object.get_discussion_url() + get_comment_query_string(page)


"""================================================== Announcement =================================================="""


class AnnouncementDetail(LoginRedirectMixin, PermissionRequiredMixin, DetailView):
    model = Announcement
    template_name = 'accounts/announcement/announcement_detail.html'
    permission_required = 'accounts.view_announcement'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        # TODO: mark corresponding notifications as read
        # Notification.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object),
        #                             object_id=object.id).mark_as_read()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = markdown(self.object.text)
        return context


class AnnouncementCreate(LoginRedirectMixin, PermissionRequiredMixin, CreateView):
    model = Announcement
    fields = ['group', 'title', 'text', 'actual']
    template_name = 'accounts/announcement/announcement_form.html'
    permission_required = 'accounts.add_announcement'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AnnouncementUpdate(LoginRedirectMixin, PermissionRequiredMixin, UpdateView):
    model = Announcement
    fields = ['group', 'title', 'text', 'actual']
    template_name = 'accounts/announcement/announcement_form.html'
    permission_required = 'accounts.change_announcement'


class AnnouncementDelete(LoginRedirectMixin, PermissionRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('accounts:announcement-list')
    template_name = 'accounts/announcement/announcement_delete.html'
    permission_required = 'accounts.delete_announcement'


class AnnouncementList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'accounts/announcement/announcement_list.html'
    context_object_name = 'announcements'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['has_actual_announcements'] = Announcement.objects.get_queryset().filter(
            actual__gte=timezone.now().today()).exists()
        return context


"""================================================== Notification =================================================="""


class NotificationList(LoginRequiredMixin, PaginatorMixin, ListView):
    model = Notification
    template_name = 'accounts/notification/notification_list.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = super().get_queryset().filter(recipient=self.request.user).actual()
        context['paginator'], context['page_obj'], context['notifications'], context['is_paginated'] = self.paginate_queryset(notifications)
        return context
