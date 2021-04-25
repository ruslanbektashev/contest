from operator import attrgetter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from markdown import markdown

from contest.mixins import LoginRedirectOwnershipOrPermissionRequiredMixin, LoginRedirectPermissionRequiredMixin
from support.models import Question, Report
from accounts.models import Activity


class Support(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'support/index.html'
    context_object_name = 'questions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reports = Report.objects.all() if self.request.user.is_superuser else Report.objects.filter(owner=self.request.user)
        context.update({
            'reports': sorted(reports, key=attrgetter('date_created'), reverse=True)
        })
        return context

    def get_queryset(self):
        questions = Question.objects.all() if self.request.user.has_perm('support.change_question') else Question.objects.filter(Q(is_published=True) | Q(owner=self.request.user))
        return questions


"""==================================================== Question ===================================================="""


class QuestionDetail(LoginRequiredMixin, DetailView):
    model = Question
    template_name = 'support/question/question_detail.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        Activity.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object), object_id=object.id).mark_as_read()
        Activity.objects.filter(recipient=request.user, subject_type=ContentType.objects.get_for_model(object), subject_id=object.id).mark_as_read()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer'] = markdown(self.object.answer)
        return context


class QuestionCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Question
    fields = ['question', 'addressee', 'answer', 'is_published', 'redirect_comment']
    template_name = 'support/question/question_form.html'
    permission_required = 'support.add_question'

    def get_form(self):
        form = super().get_form()
        perm = Permission.objects.get(content_type__app_label='support', codename='change_question')
        form.fields['addressee'].queryset = User.objects.filter(Q(user_permissions=perm))
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class QuestionUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Question
    fields = ['question', 'addressee', 'answer', 'is_published', 'redirect_comment']
    template_name = 'support/question/question_form.html'
    permission_required = 'support.change_question'


class QuestionDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Question
    success_url = reverse_lazy('support:question-list')
    template_name = 'support/question/question_delete.html'
    permission_required = 'support.delete_question'


class QuestionList(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'support/question/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        questions = Question.objects.all() if self.request.user.has_perm('support.change_question') else Question.objects.filter(Q(is_published=True) | Q(owner=self.request.user))
        return questions


"""===================================================== Report ====================================================="""


class ReportDetail(LoginRedirectOwnershipOrPermissionRequiredMixin, DetailView):
    model = Report
    template_name = 'support/report/report_detail.html'
    permission_required = 'support.view_report'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        Activity.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object), object_id=object.id).mark_as_read()
        Activity.objects.filter(recipient=request.user, subject_type=ContentType.objects.get_for_model(object), subject_id=object.id).mark_as_read()
        return super().get(request, *args, **kwargs)


class ReportCreate(LoginRequiredMixin, CreateView):
    model = Report
    template_name = 'support/report/report_form.html'
    fields = ['title', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['from_url'] = self.request.GET.get('from', '')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.page_url = self.storage['from_url']
        return super().form_valid(form)

    def get_success_url(self):
        return self.storage['from_url'] or reverse('support:report-list')


class ReportUpdate(LoginRedirectOwnershipOrPermissionRequiredMixin, UpdateView):
    model = Report
    fields = ['title', 'text', 'closed']
    success_url = reverse_lazy('support:report-list')
    template_name = 'support/report/report_form.html'
    permission_required = 'support.change_report'


class ReportDelete(LoginRedirectOwnershipOrPermissionRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy('support:report-list')
    template_name = 'support/report/report_delete.html'
    permission_required = 'support.delete_report'


class ReportList(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'support/report/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return Report.objects.filter(owner=self.request.user)
        return super().get_queryset()
