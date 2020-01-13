from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView, TemplateView
from markdown import markdown

from contest.mixins import LoginAndPermissionRequiredMixin
from support.models import Question, Report


class Support(LoginRequiredMixin, TemplateView):
    template_name = 'support/index.html'


"""==================================================== Question ===================================================="""


class QuestionDetail(LoginRequiredMixin, DetailView):
    model = Question
    template_name = 'support/question/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer'] = markdown(self.object.answer)
        return context


class QuestionCreate(LoginAndPermissionRequiredMixin, CreateView):
    model = Question
    fields = ['question', 'answer', 'is_published']
    template_name = 'support/question/question_form.html'
    permission_required = 'support.add_question'
    raise_exception = True

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class QuestionUpdate(LoginAndPermissionRequiredMixin, UpdateView):
    model = Question
    fields = ['question', 'answer', 'is_published']
    template_name = 'support/question/question_form.html'
    permission_required = 'support.change_question'
    raise_exception = True


class QuestionDelete(LoginAndPermissionRequiredMixin, DeleteView):
    model = Question
    success_url = reverse_lazy('support:question-list')
    template_name = 'support/question/question_delete.html'
    permission_required = 'support.delete_question'
    raise_exception = True


class QuestionList(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'support/question/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.filter(is_published=True)


"""===================================================== Report ====================================================="""


class ReportDetail(LoginAndPermissionRequiredMixin, DetailView):
    model = Report
    template_name = 'support/report/report_detail.html'
    permission_required = 'user.is_staff'
    raise_exception = True


class ReportCreate(LoginRequiredMixin, CreateView):
    model = Report
    template_name = 'support/report/report_form.html'
    fields = ['title', 'text']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, *args, **kwargs):
        self.storage['from_url'] = self.request.GET.get('from', '')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.page_url = self.storage['from_url']
        return super().form_valid(form)

    def get_success_url(self):
        return self.storage['from_url'] or reverse('support:report-list')


class ReportUpdate(LoginAndPermissionRequiredMixin, UpdateView):
    model = Report
    fields = ['title', 'text']
    template_name = 'support/report/report_form.html'
    permission_required = 'user.is_staff'
    raise_exception = True


class ReportDelete(LoginAndPermissionRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy('support:report-list')
    template_name = 'support/report/report_delete.html'
    permission_required = 'user.is_staff'
    raise_exception = True


class ReportList(LoginAndPermissionRequiredMixin, ListView):
    model = Report
    template_name = 'support/report/report_list.html'
    context_object_name = 'reports'
    permission_required = 'user.is_staff'
    raise_exception = True
