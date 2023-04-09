import os.path

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, DeleteView

from contest.documents.viewer import to_html
from contest.mixins import LoginRedirectMixin
from schedule.forms import ScheduleForm, ScheduleAttachmentForm, ScheduleAttachmentBaseFormSet
from schedule.models import Schedule, ScheduleAttachment


class ScheduleDetail(LoginRedirectMixin, DetailView):
    model = Schedule
    template_name = 'schedule/schedule/schedule_detail.html'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        # TODO: mark corresponding notifications as read
        # Notification.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object),
        #                             object_id=object.id).mark_as_read()
        return super().get(request, *args, **kwargs)


class ScheduleCreate(LoginRedirectMixin, PermissionRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedule/schedule/schedule_form.html'
    permission_required = 'schedule.add_schedule'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        forms_num = 12
        ScheduleAttachmentInlineFormSet = inlineformset_factory(Schedule, ScheduleAttachment,
                                                                form=ScheduleAttachmentForm,
                                                                formset=ScheduleAttachmentBaseFormSet,
                                                                fields=('name', 'file'), extra=forms_num,
                                                                min_num=1, validate_min=True,
                                                                max_num=forms_num, validate_max=True)
        inlineformset_kwargs = {'initial': [
            {'name': "ПМиИ 1"},
            {'name': "ПМиИ 2"},
            {'name': "ПМиИ 3"},
            {'name': "ПМиИ 4"},
            {'name': "ПМиИ Магистратура 1"},
            {'name': "ПМиИ Магистратура 2"},
            {'name': "Психология 1"},
            {'name': "Психология 2"},
            {'name': "Психология 3"},
            {'name': "Психология 4"},
            {'name': "Психология Магистратура 1"},
            {'name': "Психология Магистратура 2"},
        ]}
        if self.request.method == 'POST':
            inlineformset_kwargs.update({'data': self.request.POST, 'files': self.request.FILES})
        self.storage['attachment_formset'] = ScheduleAttachmentInlineFormSet(**inlineformset_kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        attachment_formset = self.storage['attachment_formset']
        if attachment_formset.is_valid():
            form.instance.owner = self.request.user
            self.object = form.save()
            attachment_formset.instance = self.object
            attachment_formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.storage['attachment_formset'] = attachment_formset
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment_formset'] = self.storage['attachment_formset']
        return context


class ScheduleDelete(LoginRedirectMixin, PermissionRequiredMixin, DeleteView):
    model = Schedule
    template_name = 'schedule/schedule/schedule_delete.html'
    permission_required = 'schedule.delete_schedule'
    success_url = reverse_lazy('schedule:schedule-list')


class ScheduleList(LoginRedirectMixin, ListView):
    model = Schedule
    template_name = 'schedule/schedule/schedule_list.html'
    context_object_name = 'schedules'


class ScheduleAttachmentDetail(LoginRedirectMixin, DetailView):
    model = ScheduleAttachment
    template_name = 'schedule/scheduleattachment/schedule_attachment_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'pdf' in os.path.splitext(self.object.file.path)[1].lower():
            return HttpResponseRedirect(self.object.file.url)
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule'] = self.object.schedule
        context['schedule_attachment_name'] = self.object.name
        context['sheet'], _ = to_html(attachment=self.object)
        return context
