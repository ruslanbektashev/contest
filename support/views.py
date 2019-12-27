from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView, TemplateView
from markdown import markdown

from .models import FAQ
from .models import Report


class Support(LoginRequiredMixin, TemplateView):
    template_name = 'support/index.html'


"""====================================================== FAQ ======================================================="""


class FAQDetail(LoginRequiredMixin, DetailView):
    model = FAQ
    template_name = 'support/faq/faq_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answer'] = markdown(self.object.answer)
        return context


class FAQCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = FAQ
    fields = ['question', 'answer', 'is_published']
    template_name = 'support/faq/faq_form.html'
    permission_required = 'support.add_faq'
    raise_exception = True

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class FAQUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = FAQ
    fields = ['question', 'answer', 'is_published']
    template_name = 'support/faq/faq_form.html'
    permission_required = 'support.change_faq'
    raise_exception = True


class FAQDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = FAQ
    success_url = reverse_lazy('support:faq-list')
    template_name = 'support/faq/faq_delete.html'
    permission_required = 'support.delete_faq'
    raise_exception = True


class FAQList(LoginRequiredMixin, ListView):
    model = FAQ
    template_name = 'support/faq/faq_list.html'
    context_object_name = 'faqs'

    def get_queryset(self):
        return FAQ.objects.filter(is_published=True)


"""===================================================== Report ====================================================="""


class ReportDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
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


class ReportUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Report
    fields = ['title', 'text']
    template_name = 'support/report/report_form.html'
    permission_required = 'user.is_staff'
    raise_exception = True


class ReportDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy('support:report-list')
    template_name = 'support/report/report_delete.html'
    permission_required = 'user.is_staff'
    raise_exception = True


class ReportList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Report
    template_name = 'support/report/report_list.html'
    context_object_name = 'reports'
    permission_required = 'user.is_staff'
    raise_exception = True
