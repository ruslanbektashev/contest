from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, RedirectView, TemplateView, UpdateView
from markdown import markdown

from contest.mixins import LoginRedirectMixin, OwnershipOrMixin, PaginatorMixin
from support.forms import QuestionForm
from support.models import Discussion, Question, Report, TutorialStepPass


class Support(LoginRequiredMixin, TemplateView):
    template_name = 'support/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_perm('support.change_question'):
            context['questions'] = Question.objects.filter(answer='')
        else:
            context['questions'] = Question.objects.filter(Q(is_published=True) | Q(owner=self.request.user))
        if self.request.user.has_perm('support.change_report'):
            context['reports'] = Report.objects.filter(closed=False)
        else:
            context['reports'] = Report.objects.filter(Q(owner=self.request.user) & Q(closed=False))
        context['discussion'] = Discussion.objects.get(id=1)
        return context


"""==================================================== Question ===================================================="""


class QuestionDetail(LoginRequiredMixin, DetailView):
    model = Question
    template_name = 'support/question/question_detail.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        # TODO: mark corresponding notifications as read
        # Notification.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object),
        #                             object_id=object.id).mark_as_read()
        # Notification.objects.filter(recipient=request.user, subject_type=ContentType.objects.get_for_model(object),
        #                             subject_id=object.id).mark_as_read()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer'] = markdown(self.object.answer)
        return context


class QuestionCreate(LoginRedirectMixin, PermissionRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'support/question/question_form.html'
    permission_required = 'support.add_question'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['addressee_queryset'] = User.objects.filter(groups__name__in=["Преподаватель", "Модератор"])
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class QuestionUpdate(LoginRedirectMixin, PermissionRequiredMixin, UpdateView):
    model = Question
    fields = ['question', 'addressee', 'answer', 'is_published', 'redirect_comment']
    template_name = 'support/question/question_form.html'
    permission_required = 'support.change_question'


class QuestionDelete(LoginRedirectMixin, PermissionRequiredMixin, DeleteView):
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


class ReportDetail(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, DetailView):
    model = Report
    template_name = 'support/report/report_detail.html'
    permission_required = 'support.view_report'

    def has_ownership(self):
        return self.get_object().owner_id == self.request.user.id

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        # TODO: mark corresponding notifications as read
        # Notification.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object),
        #                             object_id=object.id).mark_as_read()
        # Notification.objects.filter(recipient=request.user, subject_type=ContentType.objects.get_for_model(object),
        #                             subject_id=object.id).mark_as_read()
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


class ReportUpdate(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, UpdateView):
    model = Report
    fields = ['title', 'text', 'closed']
    success_url = reverse_lazy('support:report-list')
    template_name = 'support/report/report_form.html'
    permission_required = 'support.change_report'

    def has_ownership(self):
        return self.get_object().owner_id == self.request.user.id


class ReportDelete(LoginRedirectMixin, OwnershipOrMixin, PermissionRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy('support:report-list')
    template_name = 'support/report/report_delete.html'
    permission_required = 'support.delete_report'

    def has_ownership(self):
        return self.get_object().owner_id == self.request.user.id


class ReportList(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'support/report/report_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        if not self.request.user.has_perm('support.change_report'):
            return Report.objects.filter(owner=self.request.user)
        return super().get_queryset()


"""=================================================== Discussion ==================================================="""


class DiscussionDetail(LoginRedirectMixin, PermissionRequiredMixin, PaginatorMixin, DetailView):
    model = Discussion
    template_name = 'support/discussion/discussion_detail.html'
    permission_required = 'support.view_discussion'

    def get_queryset_for_paginator(self):
        return self.object.comment_set.actual().select_related('author', 'author__account')


"""===================================================== Change ====================================================="""


class ChangeList(LoginRedirectMixin, PermissionRequiredMixin, TemplateView):
    template_name = "support/change/change_list.html"
    permission_required = "contests.add_course"


"""================================================ TutorialStepPass ================================================"""


class TutorialReset(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permission_required = 'support.delete_tutorialsteppass'

    def get_redirect_url(self, *args, **kwargs):
        passed_tutorial_steps = TutorialStepPass.objects.filter(user_id=self.request.user.id)
        if kwargs['view'] != '__all__':
            passed_tutorial_steps = passed_tutorial_steps.filter(view=kwargs['view'])
        passed_tutorial_steps.delete()
        return self.request.GET.get('from')
