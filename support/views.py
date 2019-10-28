from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from markdown import markdown

from .models import FAQ

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
