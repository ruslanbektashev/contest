from pygments import highlight
from pygments.lexers import CppLexer
from pygments.formatters import HtmlFormatter

from datetime import date, datetime
from markdown import markdown

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView, FormView
from django.views.generic.detail import BaseDetailView, SingleObjectMixin

from accounts.models import Account, Activity
from contest.mixins import (LoginRedirectPermissionRequiredMixin, LoginRedirectOwnershipOrPermissionRequiredMixin,
                            PaginatorMixin)
from contests.results import TaskProgress
from contests.tasks import evaluate_submission, moss_submission
from contests.forms import (CreditSetForm, ContestForm, ProblemForm, SolutionForm, UTTestForm, FNTestForm,
                            SubmissionForm, SubmissionMossForm, AssignmentForm, AssignmentUpdateForm,
                            AssignmentSetForm, EventForm)
from contests.models import (Attachment, Course, Credit, Lecture, Contest, Problem, Solution, IOTest, UTTest, FNTest,
                             Assignment, Submission, Execution, Event)

"""=================================================== Attachment ==================================================="""


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
        context['description'] = markdown(self.object.description)
        return context


class CourseCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Course
    fields = ['title', 'description', 'level']
    template_name = 'contests/course/course_form.html'
    permission_required = 'contests.add_course'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CourseUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Course
    fields = ['title', 'description', 'level']
    template_name = 'contests/course/course_form.html'
    permission_required = 'contests.change_course'


class CourseDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('contests:course-list')
    template_name = 'contests/course/course_delete.html'
    permission_required = 'contests.delete_course'


class CourseList(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'contests/course/course_list.html'
    context_object_name = 'courses'


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
            Credit.objects.create_set(request.user, self.storage['course'],
                                      form.cleaned_data['non_credited'].union(form.cleaned_data['runner_ups']))
            form.cleaned_data['runner_ups'].level_up()
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
        context['description'] = markdown(self.object.description)
        return context


class ContestAttachment(LoginRequiredMixin, DetailView):
    model = Contest
    template_name = 'contests/contest/contest_attachment.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['attachment_id'] = kwargs.pop('attachment_id')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['attachment'] = self.object.attachment_set.get(id=self.storage['attachment_id'])
        except Attachment.DoesNotExist:
            raise Http404('Attachment with id = %s does not exist.' % self.storage['attachment_id'])
        try:
            content = context['attachment'].file.read()
        except FileNotFoundError:
            raise Http404('File %s does not exist.' % context['attachment'].filename)
        formatter = HtmlFormatter(linenos='inline', wrapcode=True)
        context['code'] = highlight(content.decode(errors='replace').replace('\t', ' ' * 4), CppLexer(), formatter)
        return context


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

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.course = self.storage['course']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context


class ContestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Contest
    form_class = ContestForm
    template_name = 'contests/contest/contest_form.html'
    permission_required = 'contests.change_contest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
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
        context['description'] = markdown(self.object.description)
        context['contest_description'] = markdown(self.object.contest.description)
        context['latest_submission'] = self.object.get_latest_submission_by(self.request.user)
        if self.request.user.has_perm('contests.view_submission_list'):
            submissions = self.object.submission_set.all()
        else:
            submissions = self.object.submission_set.filter(owner_id=self.request.user.id)
        context['paginator'], \
            context['page_obj'], \
            context['submissions'], \
            context['is_paginated'] = self.paginate_queryset(submissions)
        return context


class ProblemAttachment(LoginRequiredMixin, DetailView):
    model = Problem
    template_name = 'contests/problem/problem_attachment.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['attachment_id'] = kwargs.pop('attachment_id')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['attachment'] = self.object.attachment_set.get(id=self.storage['attachment_id'])
        except Attachment.DoesNotExist:
            raise Http404('Attachment with id = %s does not exist.' % self.storage['attachment_id'])
        try:
            content = context['attachment'].file.read()
        except FileNotFoundError:
            raise Http404('File %s does not exist.' % context['attachment'].filename)
        formatter = HtmlFormatter(linenos='inline', wrapcode=True)
        context['code'] = highlight(content.decode(errors='replace').replace('\t', ' ' * 4), CppLexer(), formatter)
        return context


class ProblemCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'contests/problem/problem_form.html'
    permission_required = 'contests.add_problem'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['contest'] = get_object_or_404(Contest, id=kwargs.pop('contest_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.contest = self.storage['contest']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.storage['contest']
        return context


class ProblemUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Problem
    form_class = ProblemForm
    template_name = 'contests/problem/problem_form.html'
    permission_required = 'contests.change_problem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.object.contest
        return context


class ProblemDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Problem
    template_name = 'contests/problem/problem_delete.html'
    permission_required = 'contests.delete_problem'

    def get_success_url(self):
        return reverse('contests:contest-detail', kwargs={'pk': self.object.contest_id})


"""==================================================== Solution ===================================================="""


class SolutionDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = Solution
    template_name = 'contests/solution/solution_detail.html'
    permission_required = 'contests.view_solution'


class SolutionCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'contests/solution/solution_form.html'
    permission_required = 'contests.add_solution'

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


class SolutionUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'contests/solution/solution_form.html'
    permission_required = 'contests.change_solution'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['problem'] = self.object.problems.first()
        return kwargs


class SolutionDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Solution
    template_name = 'contests/solution/solution_delete.html'
    permission_required = 'contests.delete_solution'

    def get_success_url(self):
        return reverse('contests:solution-detail', kwargs={'pk': self.object.problem_id})


"""===================================================== IOTest ====================================================="""


class IOTestDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = IOTest
    template_name = 'contests/iotest/iotest_detail.html'
    permission_required = 'contests.view_iotest'


class IOTestCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = IOTest
    fields = ['title', 'compile_args', 'compile_args_override', 'launch_args', 'launch_args_override', 'input', 'output']
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


class IOTestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = IOTest
    fields = ['title', 'compile_args', 'compile_args_override', 'launch_args', 'launch_args_override', 'input', 'output']
    template_name = 'contests/iotest/iotest_form.html'
    permission_required = 'contests.change_iotest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.object.problem
        return context


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


class UTTestUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = UTTest
    form_class = UTTestForm
    template_name = 'contests/uttest/uttest_form.html'
    permission_required = 'contests.change_uttest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.object.problem
        return context


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
        context['paginator'], \
            context['page_obj'], \
            context['submissions'], \
            context['is_paginated'] = self.paginate_queryset(submissions)
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
        return reverse('contests:assignment-table', kwargs={'course_id': self.storage['course'].id})


class AssignmentCreateRandomSet(LoginRedirectPermissionRequiredMixin, FormView):
    form_class = AssignmentSetForm
    template_name = 'contests/assignment/assignment_random_set_form.html'
    permission_required = 'contests.add_assignment'

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
            Assignment.objects.create_random_set(request.user, form.cleaned_data['contest'],
                                                 form.cleaned_data['limit_per_user'])
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        return context

    def get_success_url(self):
        return reverse('contests:assignment-table', kwargs={'course_id': self.storage['course'].id})


class AssignmentUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentUpdateForm
    template_name = 'contests/assignment/assignment_form.html'
    permission_required = 'contests.change_assignment'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.object.problem.contest.course
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.problem.contest.course
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
        self.storage['debts'] = request.GET.get('debts')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.storage['debts']:
            self.storage['students'] = Account.students.enrolled().debtors(self.storage['course'].level)
        else:
            self.storage['students'] = Account.students.enrolled().filter(level=self.storage['course'].level).with_credits()
        bool(self.storage['students'])  # evaluate now
        return (Assignment.objects
                .filter(user__in=self.storage['students'].values_list('user'),
                        problem__contest__course=self.storage['course'])
                .select_related('user', 'problem')
                .order_by('user__account', 'problem__contest', 'date_created'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.storage['course']
        context['students'] = self.storage['students']
        context['debts'] = self.storage['debts']
        return context


"""=================================================== Submission ==================================================="""


class SubmissionDetail(LoginRedirectOwnershipOrPermissionRequiredMixin, DetailView):
    model = Submission
    template_name = 'contests/submission/submission_detail.html'
    permission_required = 'contests.view_submission'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['from_url_name'] = request.GET.get('from', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['from_url'] = reverse('contests:' + self.storage['from_url_name'])
            context['from_url_name'] = self.storage['from_url_name']
        except NoReverseMatch:
            pass
        return context


class SubmissionDownload(LoginRedirectPermissionRequiredMixin, BaseDetailView):
    model = Submission
    permission_required = 'contests.download_submission'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(self.object.get_files_as_zip(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(self.object.pk)
        return response


class SubmissionAttachment(LoginRedirectPermissionRequiredMixin, DetailView):
    model = Submission
    template_name = 'contests/submission/submission_attachment.html'
    permission_required = 'contests.view_submission'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['attachment_id'] = kwargs.pop('attachment_id')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['attachment'] = self.object.attachment_set.get(id=self.storage['attachment_id'])
        except Attachment.DoesNotExist:
            raise Http404('Attachment with id = %s does not exist.' % self.storage['attachment_id'])
        try:
            content = context['attachment'].file.read()
        except FileNotFoundError:
            raise Http404('File %s does not exist.' % context['attachment'].filename)
        formatter = HtmlFormatter(linenos='inline', wrapcode=True)
        context['code'] = highlight(content.decode(errors='replace').replace('\t', ' ' * 4), CppLexer(), formatter)
        return context


class SubmissionCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'contests/submission/submission_form.html'
    permission_required = 'contests.add_submission'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['problem'] = get_object_or_404(Problem, id=kwargs.pop('problem_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['owner'] = self.request.user
        kwargs['problem'] = self.storage['problem']
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.problem = self.storage['problem']
        try:
            form.instance.assignment = Assignment.objects.get(user=self.request.user, problem=self.storage['problem'])
        except Assignment.DoesNotExist:
            pass
        self.object = form.save()
        if self.storage['problem'].is_testable:
            task = evaluate_submission.delay(self.object.pk, self.request.user.id)
            self.object.task_id = task.id
            self.object.save()
        Activity.objects.on_submission_created(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.storage['problem']
        return context


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
        self.storage['from_url_name'] = request.GET.get('from', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        if self.object.problem.is_testable:
            task = evaluate_submission.delay(self.object.pk, request.user.id)
            self.object.task_id = task.id
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        url = reverse('contests:submission-detail', kwargs={'pk': self.object.pk})
        if self.storage['from_url_name']:
            return url + '?from=' + self.storage['from_url_name']
        else:
            return url


def submission_get_progress(request, task_id):
    progress = TaskProgress(task_id)
    return JsonResponse(progress.get_info())


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
        return super().get_queryset().select_related('owner', 'problem')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['from_url_name'] = 'submission-list'
        return context


"""=================================================== Execution ===================================================="""


class ExecutionList(LoginRequiredMixin, ListView):
    model = Execution
    template_name = 'contests/execution/execution_list.html'
    context_object_name = 'executions'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['submission_id'] = kwargs.pop('pk')
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
        return render(request, 'contests/index.html', {'courses': Course.objects.all()})
    else:
        return redirect(reverse('contests:assignment-list'))
