from datetime import date, datetime

from django.core.exceptions import PermissionDenied
from django.forms.models import inlineformset_factory
from django.utils import timezone

from markdown import markdown
from mimetypes import guess_type
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CppLexer, TextLexer

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import BaseDetailView, SingleObjectMixin
from django.views.generic.edit import BaseCreateView, BaseDeleteView, BaseUpdateView
from django.views.generic.list import BaseListView

from accounts.models import Account, Activity, Faculty
from contest.mixins import (LoginRedirectOwnershipOrPermissionRequiredMixin, LoginRedirectPermissionRequiredMixin,
                            PaginatorMixin)
from contests.forms import (AssignmentForm, AssignmentSetForm, AssignmentUpdateForm, AssignmentUpdatePartialForm,
                            ContestForm, ContestPartialForm, CourseForm, CreditSetForm, EventForm, FNTestForm,
                            OptionBaseFormSet, OptionForm, ProblemCommonForm, ProblemProgramForm, ProblemAttachmentForm,
                            ProblemRollbackResultsForm, ProblemTestForm, SubmissionAttachmentForm, SubmissionFilesForm,
                            SubmissionMossForm, SubmissionOptionsForm, SubmissionPatternForm, SubmissionTextForm,
                            SubmissionUpdateForm, UTTestForm)
from contests.models import (Assignment, Attachment, Contest, Course, Credit, Event, Execution, FNTest, Filter, IOTest,
                             Lecture, Option, Problem, SubProblem, Submission, SubmissionPattern, UTTest)
from contests.results import TaskProgress
from contests.tasks import evaluate_submission, moss_submission

"""=================================================== Attachment ==================================================="""


class AttachmentDetail(DetailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            attachment = self.object.attachment_set.get(id=kwargs.get('attachment_id'))
        except Attachment.DoesNotExist:
            raise Http404('Attachment with id = %s does not exist.' % kwargs.get('attachment_id'))
        attachment_file_type, _ = guess_type(attachment.file.path)
        if 'x-c' not in attachment_file_type:
            return HttpResponseRedirect(attachment.file.url)
        context = self.get_context_data(object=self.object, attachment=attachment)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attachment = kwargs.get('attachment')
        try:
            content = attachment.file.read()
        except FileNotFoundError:
            raise Http404('File %s does not exist.' % attachment.filename)
        formatter = HtmlFormatter(linenos='inline', wrapcode=True)
        context['code'] = highlight(content.decode(errors='replace').replace('\t', ' ' * 4), CppLexer(), formatter)
        return context


class AttachmentDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Attachment
    template_name = 'contests/attachment/attachment_delete.html'
    permission_required = 'contests.delete_attachment'

    def get_success_url(self):
        return self.object.object.get_absolute_url()


"""===================================================== Course ====================================================="""


class CourseDetail(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'contests/course/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribers_ids'] = self.object.subscription_set.all().values_list('user', flat=True)
        if self.request.user.id in context['subscribers_ids']:
            context['subscription_id'] = self.object.subscription_set.get(user=self.request.user).id
        return context


class CourseDiscussion(LoginRequiredMixin, PaginatorMixin, DetailView):
    model = Course
    template_name = 'contests/course/course_discussion.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comment_set.actual()
        context['paginator'], context['page_obj'], context['comments'], context['is_paginated'] = \
            self.paginate_queryset(comments)
        context['subscribers_ids'] = self.object.subscription_set.all().values_list('user', flat=True)
        if self.request.user.id in context['subscribers_ids']:
            context['subscription_id'] = self.object.subscription_set.get(user=self.request.user).id
        return context


class CourseCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'contests/course/course_form.html'
    permission_required = 'contests.add_course'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        faculty_id = int(request.GET.get('faculty_id') or request.user.account.faculty_id)
        self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['faculty'] = self.storage['faculty']
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.storage['faculty']
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'contests/course/course_form.html'
    permission_required = 'contests.change_course'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.object.faculty
        return kwargs


class CourseDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('contests:course-list')
    template_name = 'contests/course/course_delete.html'
    permission_required = 'contests.delete_course'


class CourseList(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'contests/course/course_list.html'
    context_object_name = 'courses'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        faculty_id = int(request.GET.get('faculty_id') or request.user.account.faculty_id)
        self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.account.is_instructor and not self.request.user.has_perm('contests.add_faculty'):
            course_ids = self.request.user.filter_set.values_list('course', flat=True)
            courses = Course.objects.filter(id__in=course_ids)
        else:
            courses = Course.objects.filter(faculty=self.storage['faculty'])
        return courses


"""===================================================== Credit ====================================================="""


class CourseStart(LoginRedirectPermissionRequiredMixin, FormView):
    form_class = CreditSetForm
    template_name = 'contests/course/course_start_form.html'
    permission_required = 'contests.add_credit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['course'] = get_object_or_404(Course, id=kwargs.pop('course_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.storage['course']
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            Credit.objects.create_set(request.user, self.storage['course'], form.cleaned_data['runner_ups'])
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context

    def get_success_url(self):
        return reverse('contests:assignment-table', kwargs={'course_id': self.storage['course'].id})


class CreditUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Credit
    fields = ['score']
    template_name = 'contests/credit/credit_form.html'
    permission_required = 'contests.change_credit'

    def get_success_url(self):
        return reverse('contests:assignment-table', kwargs={'course_id': self.object.course_id})


class CreditDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Credit
    template_name = 'contests/credit/credit_delete.html'
    permission_required = 'contests.delete_credit'

    def get_success_url(self):
        return reverse('contests:assignment-table', kwargs={'course_id': self.object.course_id})


"""===================================================== Filter ====================================================="""


class FilterCreate(LoginRedirectPermissionRequiredMixin, BaseCreateView):
    model = Filter
    http_method_names = ['get']
    success_url = reverse_lazy('contests:filter-table')
    permission_required = 'contests.add_filter'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs.get('user_id'))
        course = get_object_or_404(Course, id=kwargs.get('course_id'))
        if not Filter.objects.filter(user=user, course=course).exists():
            Filter.objects.create(user=user, course=course)
        return HttpResponseRedirect(self.success_url)


class FilterDelete(LoginRedirectPermissionRequiredMixin, BaseDeleteView):
    model = Filter
    http_method_names = ['get']
    success_url = reverse_lazy('contests:filter-table')
    permission_required = 'contests.delete_filter'

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class FilterTable(LoginRedirectPermissionRequiredMixin, TemplateView):
    template_name = 'contests/filter/filter_table.html'
    permission_required = 'contests.view_filter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.filter(groups__name__in=["Преподаватель", "Модератор"])
        courses = Course.objects.all()
        table = []
        for i in range(len(users)):
            row = []
            for j in range(len(courses)):
                col = {}
                try:
                    _filter = Filter.objects.get(user=users[i], course=courses[j])
                    col['exists'] = True
                    col['params'] = {'id': _filter.id}
                except Filter.DoesNotExist:
                    col['exists'] = False
                    col['params'] = {'user_id': users[i].id, 'course_id': courses[j].id}
                row.append(col)
            table.append({'user': users[i], 'cols': row})
        context['users'] = users
        context['courses'] = courses
        context['table'] = table
        return context


"""===================================================== Lecture ===================================================="""


class LectureDetail(LoginRequiredMixin, DetailView):
    model = Lecture
    template_name = 'contests/lecture/lecture_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['description'] = markdown(self.object.description)
        return context


class LectureCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Lecture
    fields = ['title', 'description']
    template_name = 'contests/lecture/lecture_form.html'
    permission_required = 'contests.add_lecture'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['course'] = get_object_or_404(Course, id=kwargs.pop('course_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.course = self.storage['course']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context


class LectureUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Lecture
    fields = ['title', 'description']
    template_name = 'contests/lecture/lecture_form.html'
    permission_required = 'contests.change_lecture'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context


class LectureDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Lecture
    template_name = 'contests/lecture/lecture_delete.html'
    permission_required = 'contests.delete_lecture'

    def get_success_url(self):
        return reverse('contests:course-detail', kwargs={'pk': self.object.course_id})


"""===================================================== Contest ===================================================="""


class ContestDetail(LoginRequiredMixin, DetailView):
    model = Contest
    template_name = 'contests/contest/contest_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribers_ids'] = self.object.subscription_set.all().values_list('user', flat=True)
        if self.request.user.id in context['subscribers_ids']:
            context['subscription_id'] = self.object.subscription_set.get(user=self.request.user).id
        return context


class ContestDiscussion(LoginRequiredMixin, PaginatorMixin, DetailView):
    model = Contest
    template_name = 'contests/contest/contest_discussion.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comment_set.actual()
        context['paginator'], context['page_obj'], context['comments'], context['is_paginated'] = \
            self.paginate_queryset(comments)
        return context


class ContestAttachment(LoginRequiredMixin, AttachmentDetail):
    model = Contest
    template_name = 'contests/contest/contest_attachment.html'


class ContestCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Contest
    form_class = ContestForm
    template_name = 'contests/contest/contest_form.html'
    permission_required = 'contests.add_contest'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['course'] = get_object_or_404(Course, id=kwargs.pop('course_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['course'] = self.storage['course']
        initial['number'] = Contest.objects.get_new_number(self.storage['course'])
        initial['title'] = "Раздел " + str(initial['number'])
        return initial

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context


class ContestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Contest
    template_name = 'contests/contest/contest_form.html'
    permission_required = 'contests.change_contest'

    def get_form_class(self):
        if self.request.GET.get('add_files') == '1':
            return ContestPartialForm
        return ContestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        if self.request.GET.get('add_files') == '1':
            context['add_files'] = True
        return context


class ContestDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Contest
    template_name = 'contests/contest/contest_delete.html'
    permission_required = 'contests.delete_contest'

    def get_success_url(self):
        return reverse('contests:course-detail', kwargs={'pk': self.object.course_id})


"""===================================================== Problem ===================================================="""


class ProblemDetail(LoginRequiredMixin, PaginatorMixin, DetailView):
    model = Problem
    template_name = 'contests/problem/problem_detail.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_submission'] = self.object.get_latest_submission_by(self.request.user)
        if self.request.user.has_perm('contests.view_submission_list'):
            submissions = self.object.submission_set.all()
        else:
            submissions = self.object.submission_set.filter(owner_id=self.request.user.id)
        context['paginator'], context['page_obj'], context['submissions'], context['is_paginated'] = \
            self.paginate_queryset(submissions)
        if self.object.type == 'Test':
            context['subproblems'] = SubProblem.objects.filter(problem=self.object).select_related('sub_problem')
        return context


class ProblemDiscussion(LoginRequiredMixin, PaginatorMixin, DetailView):
    model = Problem
    template_name = 'contests/problem/problem_discussion.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comment_set.actual()
        context['paginator'], context['page_obj'], context['comments'], context['is_paginated'] = \
            self.paginate_queryset(comments)
        return context


class ProblemAttachment(LoginRequiredMixin, AttachmentDetail):
    model = Problem
    template_name = 'contests/problem/problem_attachment.html'


class ProblemRollbackResults(LoginRedirectPermissionRequiredMixin, FormView):
    form_class = ProblemRollbackResultsForm
    template_name = 'contests/problem/problem_rollback_results_form.html'
    permission_required = 'contests.change_problem'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem_id'] = self.kwargs.get('pk')
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            submissions = form.cleaned_data['submissions']
            assignments = Assignment.objects.to_rollback(submissions)
            submissions.rollback_status()
            assignments.rollback_score()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = get_object_or_404(Problem, id=self.kwargs.get('pk'))
        return context

    def get_success_url(self):
        return get_object_or_404(Problem, id=self.kwargs.get('pk')).get_absolute_url()


class ProblemCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Problem
    template_name = 'contests/problem/problem_form.html'
    permission_required = 'contests.add_problem'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['contest'] = get_object_or_404(Contest, id=kwargs.pop('contest_id'))
        self.storage['type'] = kwargs.get('type')
        if self.storage['type'] == 'Options':
            OptionFormSet = inlineformset_factory(parent_model=Problem, model=Option, form=OptionForm,
                                                  formset=OptionBaseFormSet, fields=('text', 'is_correct'), extra=0,
                                                  min_num=2, max_num=20, validate_min=True, validate_max=True)
            if request.method == 'GET':
                formset = OptionFormSet()
            else:
                formset = OptionFormSet(data=request.POST, files=request.FILES)
            self.storage['formset'] = formset
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.storage['type'] == 'Program':
            return ProblemProgramForm
        elif self.storage['type'] == 'Test':
            return ProblemTestForm
        else:
            return ProblemCommonForm

    def get_initial(self):
        initial = super().get_initial()
        initial['contest'] = self.storage['contest']
        initial['type'] = self.storage['type']
        initial['number'] = Problem.objects.get_new_number(self.storage['contest'])
        if self.storage['type'] == 'Program':
            initial['title'] = "Задача "
        elif self.storage['type'] == 'Test':
            initial['title'] = "Тест "
        else:
            initial['title'] = "Вопрос "
        initial['title'] += str(initial['number'])
        return initial

    def form_valid(self, form):
        form.instance.owner = self.request.user
        if self.storage['type'] == 'Options':
            formset = self.storage.get('formset')
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                return HttpResponseRedirect(self.get_success_url())
            else:
                self.storage['formset'] = formset
                return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.storage['contest']
        context['type'] = self.storage['type']
        context['formset'] = self.storage.get('formset')
        return context

    def get_success_url(self):
        return reverse('contests:contest-detail', kwargs={'pk': self.object.contest_id})


class ProblemUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Problem
    template_name = 'contests/problem/problem_form.html'
    permission_required = 'contests.change_problem'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        problem = self.get_object()
        if problem.type == 'Options':
            OptionFormSet = inlineformset_factory(parent_model=Problem, model=Option, form=OptionForm,
                                                  formset=OptionBaseFormSet, fields=('text', 'is_correct'), extra=0,
                                                  min_num=2, max_num=20, validate_min=True, validate_max=True)
            if request.method == 'GET':
                formset = OptionFormSet(instance=problem)
            else:
                formset = OptionFormSet(data=request.POST, files=request.FILES, instance=problem)
            self.storage['formset'] = formset
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.request.GET.get('add_files') == '1':
            return ProblemAttachmentForm
        elif self.object.type == 'Program':
            return ProblemProgramForm
        elif self.object.type == 'Test':
            return ProblemTestForm
        else:
            return ProblemCommonForm

    def form_valid(self, form):
        if self.object.type == 'Options':
            formset = self.storage.get('formset')
            if formset.is_valid():
                self.object = form.save()
                formset.save()
                return HttpResponseRedirect(self.get_success_url())
            else:
                self.storage['formset'] = formset
                return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.object.contest
        context['type'] = self.object.type
        context['formset'] = self.storage.get('formset')
        if self.request.GET.get('add_files') == '1':
            context['add_files'] = True
        return context


class ProblemDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Problem
    template_name = 'contests/problem/problem_delete.html'
    permission_required = 'contests.delete_problem'

    def get_success_url(self):
        return reverse('contests:contest-detail', kwargs={'pk': self.object.contest_id})


"""=================================================== SubProblem ==================================================="""


class SubProblemUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = SubProblem
    fields = ['number']
    template_name = 'contests/subproblem/subproblem_form.html'
    permission_required = 'contests.change_subproblem'

    def get_success_url(self):
        return reverse('contests:problem-detail', kwargs={'pk': self.object.problem_id})


class SubProblemDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = SubProblem
    template_name = 'contests/subproblem/subproblem_delete.html'
    permission_required = 'contests.delete_subproblem'

    def get_success_url(self):
        return reverse('contests:problem-detail', kwargs={'pk': self.object.problem_id})


"""=============================================== SubmissionPattern ================================================"""


class SubmissionPatternDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = SubmissionPattern
    context_object_name = 'submission_pattern'
    template_name = 'contests/submission_pattern/submission_pattern_detail.html'
    permission_required = 'contests.view_submission_pattern'


class SubmissionPatternCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = SubmissionPattern
    form_class = SubmissionPatternForm
    template_name = 'contests/submission_pattern/submission_pattern_form.html'
    permission_required = 'contests.add_submission_pattern'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['problem'] = get_object_or_404(Problem, id=kwargs.pop('problem_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.storage['problem']
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.problem = self.storage['problem']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.storage['problem']
        return context


class SubmissionPatternUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = SubmissionPattern
    form_class = SubmissionPatternForm
    context_object_name = 'submission_pattern'
    template_name = 'contests/submission_pattern/submission_pattern_form.html'
    permission_required = 'contests.change_submission_pattern'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.object.problems.first()
        return kwargs


class SubmissionPatternDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = SubmissionPattern
    context_object_name = 'submission_pattern'
    template_name = 'contests/submission_pattern/submission_pattern_delete.html'
    permission_required = 'contests.delete_submission_pattern'

    def get_success_url(self):
        return reverse('contests:submission-pattern-detail', kwargs={'pk': self.object.problem_id})


"""===================================================== IOTest ====================================================="""


class IOTestDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = IOTest
    template_name = 'contests/iotest/iotest_detail.html'
    permission_required = 'contests.view_iotest'


class IOTestCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = IOTest
    fields = ['title', 'compile_args', 'compile_args_override', 'launch_args', 'launch_args_override', 'input',
              'output']
    template_name = 'contests/iotest/iotest_form.html'
    permission_required = 'contests.add_iotest'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['problem'] = get_object_or_404(Problem, id=kwargs.pop('problem_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.problem = self.storage['problem']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.storage['problem']
        return context

    def get_success_url(self):
        if Submission.objects.to_rollback(self.object.problem_id).exists():
            return reverse('contests:problem-rollback-results', kwargs={'pk': self.object.problem_id})
        else:
            super().get_success_url()


class IOTestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = IOTest
    fields = ['title', 'compile_args', 'compile_args_override', 'launch_args', 'launch_args_override', 'input',
              'output']
    template_name = 'contests/iotest/iotest_form.html'
    permission_required = 'contests.change_iotest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.object.problem
        return context

    def get_success_url(self):
        if Submission.objects.to_rollback(self.object.problem_id).exists():
            return reverse('contests:problem-rollback-results', kwargs={'pk': self.object.problem_id})
        else:
            super().get_success_url()


class IOTestDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = IOTest
    template_name = 'contests/iotest/iotest_delete.html'
    permission_required = 'contests.delete_iotest'

    def get_success_url(self):
        return reverse('contests:problem-detail', kwargs={'pk': self.object.problem_id})


"""===================================================== UTTest ====================================================="""


class UTTestDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = UTTest
    template_name = 'contests/uttest/uttest_detail.html'
    permission_required = 'contests.view_uttest'


class UTTestAttachment(LoginRequiredMixin, AttachmentDetail):
    model = Problem
    template_name = 'contests/uttest/uttest_attachment.html'


class UTTestCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = UTTest
    form_class = UTTestForm
    template_name = 'contests/uttest/uttest_form.html'
    permission_required = 'contests.add_uttest'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['problem'] = get_object_or_404(Problem, id=kwargs.pop('problem_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.problem = self.storage['problem']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.storage['problem']
        return context

    def get_success_url(self):
        if Submission.objects.to_rollback(self.object.problem_id).exists():
            return reverse('contests:problem-rollback-results', kwargs={'pk': self.object.problem_id})
        else:
            super().get_success_url()


class UTTestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = UTTest
    form_class = UTTestForm
    template_name = 'contests/uttest/uttest_form.html'
    permission_required = 'contests.change_uttest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.object.problem
        return context

    def get_success_url(self):
        if Submission.objects.to_rollback(self.object.problem_id).exists():
            return reverse('contests:problem-rollback-results', kwargs={'pk': self.object.problem_id})
        else:
            super().get_success_url()


class UTTestDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = UTTest
    template_name = 'contests/uttest/uttest_delete.html'
    permission_required = 'contests.delete_uttest'

    def get_success_url(self):
        return reverse('contests:problem-detail', kwargs={'pk': self.object.problem_id})


"""===================================================== FNTest ====================================================="""


class FNTestDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = FNTest
    template_name = 'contests/fntest/fntest_detail.html'
    permission_required = 'contests.view_fntest'


class FNTestCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = FNTest
    form_class = FNTestForm
    template_name = 'contests/fntest/fntest_form.html'
    permission_required = 'contests.add_fntest'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['problem'] = get_object_or_404(Problem, id=kwargs.pop('problem_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.storage['problem']
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.problem = self.storage['problem']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.storage['problem']
        return context


class FNTestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = FNTest
    form_class = FNTestForm
    template_name = 'contests/fntest/fntest_form.html'
    permission_required = 'contests.change_fntest'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.object.problems.first()
        return kwargs


class FNTestDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = FNTest
    template_name = 'contests/fntest/fntest_delete.html'
    permission_required = 'contests.delete_fntest'

    def get_success_url(self):
        return reverse('contests:problem-detail', kwargs={'pk': self.object.problem_id})


"""=================================================== Assignment ==================================================="""


class AssignmentDetail(LoginRequiredMixin, PaginatorMixin, DetailView):
    model = Assignment
    template_name = 'contests/assignment/assignment_detail.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submissions = self.object.get_submissions()
        context['paginator'], context['page_obj'], context['submissions'], context['is_paginated'] = \
            self.paginate_queryset(submissions)
        context['current_time'] = timezone.now()
        return context


class AssignmentDiscussion(LoginRequiredMixin, PaginatorMixin, DetailView):
    model = Assignment
    template_name = 'contests/assignment/assignment_discussion.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comment_set.actual()
        context['paginator'], context['page_obj'], context['comments'], context['is_paginated'] = \
            self.paginate_queryset(comments)
        return context


class AssignmentCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'contests/assignment/assignment_form.html'
    permission_required = 'contests.add_assignment'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['course'] = get_object_or_404(Course, id=kwargs.pop('course_id'))
        self.storage['debts'] = bool(request.GET.get('debts'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        contest_id, user_id = request.GET.get('contest_id'), request.GET.get('user_id')
        if contest_id and user_id:
            self.storage['user'] = get_object_or_404(User, id=user_id)
            self.storage['contest'] = get_object_or_404(Contest, id=contest_id)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.storage)
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context

    def get_success_url(self):
        url = reverse('contests:assignment-table', kwargs={'course_id': self.storage['course'].id})
        if self.storage['debts']:
            url += "?debts=1"
        return url


class AssignmentCreateRandomSet(LoginRedirectPermissionRequiredMixin, FormView):
    form_class = AssignmentSetForm
    template_name = 'contests/assignment/assignment_random_set_form.html'
    permission_required = 'contests.add_assignment'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['course'] = get_object_or_404(Course, id=kwargs.pop('course_id'))
        self.storage['debts'] = bool(request.GET.get('debts'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.storage['course']
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            Assignment.objects.create_random_set(request.user, form.cleaned_data['contest'], form.cleaned_data['type'],
                                                 form.cleaned_data['limit_per_user'],
                                                 form.cleaned_data['submission_limit'], form.cleaned_data['deadline'],
                                                 self.storage['debts'])
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context

    def get_success_url(self):
        url = reverse('contests:assignment-table', kwargs={'course_id': self.storage['course'].id})
        if self.storage['debts']:
            url += "?debts=1"
        return url


class AssignmentUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Assignment
    template_name = 'contests/assignment/assignment_form.html'
    permission_required = 'contests.change_assignment'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['partial'] = int(request.GET.get('partial') or 0)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.storage['partial']:
            return AssignmentUpdatePartialForm
        else:
            return AssignmentUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.storage['partial']:
            kwargs['course'] = self.object.problem.contest.course
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.problem.contest.course
        context['partial'] = self.storage['partial']
        return context


class AssignmentDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'contests/assignment/assignment_delete.html'
    permission_required = 'contests.delete_assignment'

    def get_success_url(self):
        return reverse('contests:assignment-table', kwargs={'course_id': self.object.problem.contest.course_id})


class AssignmentUserTable(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'contests/assignment/assignment_user_base.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return (Assignment.objects
                .filter(user=self.request.user)
                .select_related('problem', 'problem__contest')
                .order_by('-problem__contest__course', '-problem__contest', '-date_created'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['credits'] = self.request.user.credit_set.select_related('course')
        return context


class AssignmentCourseTable(LoginRedirectPermissionRequiredMixin, ListView):
    model = Assignment
    template_name = 'contests/assignment/assignment_course_base.html'
    context_object_name = 'assignments'
    permission_required = 'contests.view_assignment_table'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['course'] = get_object_or_404(Course, id=kwargs.pop('course_id'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.storage['debts'] = bool(request.GET.get('debts'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        course = self.storage['course']
        if self.storage['debts']:
            self.storage['students'] = Account.students.enrolled().debtors(course)
        else:
            self.storage['students'] = Account.students.enrolled().current(course)
        bool(self.storage['students'])  # evaluate now
        return Assignment.objects.for_course_table(course, self.storage['students'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        context['students'] = self.storage['students']
        context['debts'] = self.storage['debts']
        return context


"""=================================================== Submission ==================================================="""


class SubmissionDetail(LoginRedirectOwnershipOrPermissionRequiredMixin, PaginatorMixin, DetailView):
    model = Submission
    template_name = 'contests/submission/submission_detail.html'
    permission_required = 'contests.view_submission'
    paginate_by = 30

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['from_url'] = request.GET.get('from', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        Activity.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(self.object), object_id=self.object.id).mark_as_read()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['from_url'] = self.storage['from_url']
        comments = self.object.comment_set.actual()
        context['paginator'], context['page_obj'], context['comments'], context['is_paginated'] = \
            self.paginate_queryset(comments)
        return context


class SubmissionDownload(LoginRedirectPermissionRequiredMixin, BaseDetailView):
    model = Submission
    permission_required = 'contests.download_submission'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(self.object.get_files_as_zip(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(self.object.pk)
        return response


class SubmissionAttachment(LoginRedirectPermissionRequiredMixin, AttachmentDetail):
    model = Submission
    template_name = 'contests/submission/submission_attachment.html'
    permission_required = 'contests.view_submission'


class SubmissionCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Submission
    template_name = 'contests/submission/submission_form.html'
    permission_required = 'contests.add_submission'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        problem = get_object_or_404(Problem, id=kwargs.pop('problem_id'))

        try:
            assignment = Assignment.objects.get(user=self.request.user, problem=problem)
        except Assignment.DoesNotExist:
            assignment = None

        self.storage['assignment'] = assignment

        if assignment:
            nsubmissions = Submission.objects.filter(owner=self.request.user, problem=problem).count()
            if nsubmissions >= assignment.submission_limit:
                raise PermissionDenied()

        if problem.type == 'Test':
            self.storage['main_problem'] = problem
            main_submission_id = kwargs.pop('submission_id', None)
            if main_submission_id:
                main_submission = get_object_or_404(Submission, id=main_submission_id)
                self.storage['main_submission'] = main_submission
                current_problem = problem.sub_problems.exclude(submission__in=main_submission.sub_submissions.all()).first()
                if not current_problem:
                    return HttpResponseRedirect(reverse('contests:submission-detail', kwargs={'pk': main_submission.id}))
                self.storage['problem'] = current_problem
            else:
                self.storage['problem'] = problem.sub_problems.first()
        else:
            self.storage['problem'] = problem
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['owner'] = self.request.user
        kwargs['problem'] = self.storage['problem']
        kwargs['assignment'] = self.storage['assignment']
        return kwargs

    def get_form_class(self):
        problem = self.storage['problem']
        if problem.type == 'Text':
            return SubmissionTextForm
        elif problem.type == 'Options':
            return SubmissionOptionsForm
        elif problem.type == 'Files':
            return SubmissionFilesForm
        else:
            return SubmissionAttachmentForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.problem = self.storage['problem']

        if 'main_problem' in self.storage:
            if 'main_submission' not in self.storage:
                self.storage['main_submission'] = Submission.objects.create(problem=self.storage.get('main_problem'),
                                                                            owner=self.request.user,
                                                                            assignment=self.storage['assignment'])
        else:
            form.instance.assignment = self.storage['assignment']
        form.instance.main_submission = self.storage.get('main_submission')

        self.object = form.save()
        if self.object.problem.type == 'Program' and self.object.problem.is_testable:
            task = evaluate_submission.delay(self.object.pk, self.request.user.id)
            self.object.task_id = task.id
            self.object.save()
        if self.object.problem.type == 'Options':
            self.object.update_options_score()
        Activity.objects.on_submission_created(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.storage['problem']
        context['assignment'] = self.storage['assignment']
        context['main_problem'] = self.storage.get('main_problem')
        context['current_time'] = timezone.now()
        return context

    def get_success_url(self):
        if 'main_problem' in self.storage:
            main_submission = self.storage['main_submission']
            return reverse('contests:submission-continue',
                           kwargs={'problem_id': main_submission.problem.id, 'submission_id': main_submission.id})
        return super().get_success_url()


class SubmissionUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Submission
    form_class = SubmissionUpdateForm
    template_name = 'contests/submission/submission_update_form.html'
    permission_required = 'contests.change_submission'

    def form_valid(self, form):
        self.object = form.save()
        if self.object.main_submission is not None:
            self.object.main_submission.update_test_score()
        return HttpResponseRedirect(self.get_success_url())


class SubmissionMoss(LoginRedirectPermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Submission
    form_class = SubmissionMossForm
    template_name = 'contests/submission/submission_moss_form.html'
    permission_required = 'contests.moss_submission'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        to_submission_ids = list(form.cleaned_data['to_submissions'].values_list('id', flat=True))
        self.object.moss_to_submissions = ','.join(map(str, to_submission_ids))
        self.object.moss_report_url = None
        self.object.save()
        moss_submission.delay(self.object.id, to_submission_ids)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['submission'] = self.object
        return kwargs

    def get_success_url(self):
        return reverse('contests:submission-detail', kwargs={'pk': self.kwargs['pk']})


class SubmissionEvaluate(LoginRedirectOwnershipOrPermissionRequiredMixin, UpdateView):
    model = Submission
    http_method_names = ['get']
    permission_required = 'contests.evaluate_submission'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['from_url'] = request.GET.get('from', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        if self.object.problem.type == 'Program' and self.object.problem.is_testable:
            task = evaluate_submission.delay(self.object.pk, request.user.id)
            self.object.task_id = task.id
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = reverse('contests:submission-detail', kwargs={'pk': self.object.pk})
        if self.storage['from_url']:
            return url + '?from=' + self.storage['from_url']
        else:
            return url


def submission_get_progress(request, task_id):
    progress = TaskProgress(task_id)
    return JsonResponse(progress.get_info())


class SubmissionClearTask(LoginRedirectOwnershipOrPermissionRequiredMixin, BaseUpdateView):
    model = Submission
    http_method_names = ['get']
    permission_required = 'contests.evaluate_submission'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['from_url'] = request.GET.get('from', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        self.object.task_id = None
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = reverse('contests:submission-detail', kwargs={'pk': self.object.pk})
        if self.storage['from_url']:
            return url + '?from=' + self.storage['from_url']
        else:
            return url


class SubmissionDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Submission
    template_name = 'contests/submission/submission_delete.html'
    permission_required = 'contests.delete_submission'

    def get_success_url(self):
        return reverse('contests:assignment-table', kwargs={'course_id': self.object.problem.contest.course_id})


class SubmissionList(LoginRedirectPermissionRequiredMixin, ListView):
    model = Submission
    template_name = 'contests/submission/submission_list.html'
    context_object_name = 'submissions'
    paginate_by = 20
    permission_required = 'contests.view_submission_list'

    def get_queryset(self):
        course_id = self.kwargs.get('course_id', None)
        queryset = super().get_queryset().select_related('owner', 'problem', 'problem__contest')
        if course_id:
            queryset = queryset.filter(problem__contest__course_id=course_id)
        else:
            course_ids = self.request.user.filter_set.values_list('course_id')
            queryset = (queryset.filter(problem__contest__course_id__in=course_ids)
                        .select_related('problem__contest__course'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id', None)
        if course_id:
            context['course'] = get_object_or_404(Course, id=course_id)
        return context


class SubmissionBackup(LoginRedirectPermissionRequiredMixin, BaseListView):
    model = Submission
    permission_required = 'contests.download_submission'

    def dispatch(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id', None)
        if not Course.objects.filter(id=course_id).exists():
            raise Http404("Course does not exist")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        course_id = self.kwargs.get('course_id', None)
        response = HttpResponse(Submission.objects.backup(self.object_list), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(course_id)
        return response

    def get_queryset(self):
        course_id = self.kwargs.get('course_id', None)
        queryset = super().get_queryset().filter(problem__contest__course_id=course_id).select_related('problem')
        return queryset


"""=================================================== Execution ===================================================="""


class ExecutionList(LoginRequiredMixin, ListView):
    model = Execution
    template_name = 'contests/execution/execution_list.html'
    context_object_name = 'executions'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['submission_id'] = kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Execution.objects.filter(submission_id=self.storage['submission_id'])


"""===================================================== Event ======================================================"""


class EventDetail(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'contests/event/event_detail.html'


class EventCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'contests/event/event_form.html'
    permission_required = 'contests.add_event'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def get(self, request, *args, **kwargs):
        date_started, date_ended = request.GET.get('date_start'), request.GET.get('date_end')
        if date_started and date_ended:
            self.storage['date_start'] = datetime.strptime(date_started, "%Y-%m-%dT%H:%M:%S")
            self.storage['date_end'] = datetime.strptime(date_ended, "%Y-%m-%dT%H:%M:%S")
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        initial = {
            'tutor': self.request.user
        }
        if 'date_start' in self.storage and 'date_end' in self.storage:
            initial['date_start'] = self.storage['date_start']
            initial['date_end'] = self.storage['date_end']
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = initial
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        iso_date = self.object.date_start.date().isocalendar()
        return reverse('contests:event-schedule') + '?year=' + str(iso_date[0]) + '&week=' + str(iso_date[1])


class EventUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'contests/event/event_form.html'
    permission_required = 'contests.change_event'

    def get_form_kwargs(self):
        initial = {
            'tutor': self.request.user
        }
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = initial
        return kwargs


class EventDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('contests:event-list')
    template_name = 'contests/event/event_delete.html'
    permission_required = 'contests.delete_event'


class EventSchedule(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'contests/event/event_schedule.html'
    context_object_name = 'events'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        iso_today = list(date.today().isocalendar())
        if iso_today[2] == 7:
            iso_today[1] += 1
        self.storage['year'] = int(self.request.GET.get('year') or iso_today[0])
        self.storage['week'] = int(self.request.GET.get('week') or iso_today[1])
        if self.storage['week'] > 52:
            last_week = date(self.storage['year'], 12, 28).isocalendar()[1]
            if self.storage['week'] > last_week:
                self.storage['year'] += 1
                self.storage['week'] = 1
        elif self.storage['week'] < 1:
            last_week = date(self.storage['year'] - 1, 12, 28).isocalendar()[1]
            self.storage['year'] -= 1
            self.storage['week'] = last_week
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.weekly(self.storage['year'], self.storage['week'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.storage['year']
        context['week'] = self.storage['week']
        return context


"""==================================================== Specific ===================================================="""


@login_required
def index(request):
    if request.user.has_perm('contests.view_assignment_table'):
        course_ids = request.user.filter_set.values_list('course_id')
        faculty_id = int(request.GET.get('faculty_id') or request.user.account.faculty_id)
        courses = Course.objects.filter(faculty_id=faculty_id, id__in=course_ids)
        faculties = Faculty.objects.all()
        return render(request, 'contests/index.html', {'courses': courses, 'faculties': faculties})
    else:
        return redirect(reverse('contests:assignment-list'))
