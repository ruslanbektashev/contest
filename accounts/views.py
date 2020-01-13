from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView, FormView, TemplateView
from django.views.generic.list import BaseListView
from markdown import markdown

from contest.mixins import LoginAndPermissionRequiredMixin, PaginatorMixin
from accounts.forms import AccountForm, AccountListForm, AccountSetForm, ActivityMarkForm, CommentForm
from accounts.models import Account, Activity, Comment, Message, Chat, Announcement

"""==================================================== Account ====================================================="""


class AccountDetail(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account/account_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = (self.object.user.assignment_set
            .select_related('problem', 'problem__contest', 'problem__contest__course')
            .order_by('-problem__contest__course', '-problem__contest', '-date_created'))
        context['credits'] = self.object.user.credit_set.select_related('course')
        return context


class AccountUpdate(LoginAndPermissionRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account/account_form.html'
    permission_required = 'auth.change_user_email'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_staff and request.user.id != self.object.user.id:
            return self.handle_no_permission()
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        self.initial['email'] = self.object.email
        return super().get_initial()


class AccountFormList(LoginAndPermissionRequiredMixin, BaseListView, FormView):
    model = Account
    form_class = AccountListForm
    template_name = 'accounts/account/account_list.html'
    context_object_name = 'accounts'
    permission_required = 'accounts.change_account'
    raise_exception = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, *args, **kwargs):
        self.storage['level'] = int(self.request.GET.get('level') or 1)
        enrolled, graduated = self.request.GET.get('enrolled'), self.request.GET.get('graduated')
        if enrolled is not None and enrolled == '0':
            self.storage['enrolled'] = False
            self.storage['graduated'] = False
        if graduated is not None and graduated == '1':
            self.storage['enrolled'] = False
            self.storage['graduated'] = True
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            action = request.POST.get('action')
            accounts = form.cleaned_data['accounts']
            if action == 'level_up':
                accounts.level_up()
            elif action == 'level_down':
                accounts.level_down()
            elif action == 'reset_password':
                self.request.session['credentials'] = accounts.reset_password()
                return HttpResponseRedirect(reverse('accounts:account-credentials'))
            elif action == 'enroll':
                accounts.enroll()
            elif action == 'expel':
                accounts.expel()
            elif action == 'graduate':
                accounts.graduate()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))

    def get_queryset(self):
        if 'enrolled' in self.storage and 'graduated' in self.storage:
            return Account.students.filter(enrolled=self.storage['enrolled'], graduated=self.storage['graduated'])
        return Account.students.enrolled().filter(level=self.storage['level'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Account.LEVEL_CHOICES
        context.update(self.storage)
        return context

    def get_success_url(self):
        return self.request.get_full_path()


class AccountCredentials(LoginAndPermissionRequiredMixin, TemplateView):
    template_name = 'accounts/account/account_credentials.html'
    permission_required = 'accounts.add_account'
    raise_exception = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, *args, **kwargs):
        self.storage['credentials'] = self.request.session.pop('credentials', None)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['credentials'] = self.storage.pop('credentials')
        return context


class AccountCreateSet(LoginAndPermissionRequiredMixin, FormView):
    form_class = AccountSetForm
    template_name = 'accounts/account/account_set_form.html'
    permission_required = 'accounts.add_account'
    raise_exception = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, *args, **kwargs):
        self.storage['level'] = int(self.request.GET.get('level') or 1)
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['level'] = self.storage['level']
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            _, self.request.session['credentials'] = Account.students.create_set(
                form.cleaned_data['level'],
                form.cleaned_data['admission_year'],
                form.cleaned_data['names']
            )
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse('accounts:account-credentials')


"""==================================================== Activity ===================================================="""


class ActivityList(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'accounts/activity/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(recipient=self.request.user).actual()


class ActivityMark(LoginAndPermissionRequiredMixin, FormView):
    form_class = ActivityMarkForm
    http_method_names = ['post']
    template_name = 'accounts/activity/activity_list.html'
    permission_required = 'accounts.change_activity'
    raise_exception = True

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            mark = request.POST.get('mark')
            choices = form.cleaned_data['choices']
            if mark == 'read':
                choices.mark_as_read()
            elif mark == 'delete':
                choices.mark_as_deleted()
        return self.form_valid(form)

    def get_success_url(self):
        return reverse('accounts:activity-list')


"""==================================================== Comment ====================================================="""


class CommentCreate(LoginAndPermissionRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'accounts/comment/comment_reply.html'
    permission_required = 'accounts.add_comment'
    raise_exception = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, *args, **kwargs):
        try:
            self.storage['parent'] = Comment.objects.get(id=kwargs.pop('parent_id', 0))
        except Comment.DoesNotExist:
            pass
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent'] = self.storage.get('parent', None)
        return context

    def get_success_url(self):
        return self.object.object.get_absolute_url() + '#comment_' + str(self.object.id)


"""==================================================== Message ====================================================="""


class MessageCreate(LoginAndPermissionRequiredMixin, PaginatorMixin, CreateView):
    model = Message
    fields = ['text']
    template_name = 'accounts/message/message_form.html'
    permission_required = 'accounts.add_message'
    raise_exception = True
    # TODO: set proper items-per-page
    paginate_by = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, *args, **kwargs):
        self.storage['recipient'] = get_object_or_404(User, id=kwargs.pop('user_id'))
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = self.storage['recipient']
        response = super().form_valid(form)
        Chat.objects.update_or_create_chat(
            self.request.user,
            self.storage['recipient'],
            self.object
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipient'] = self.storage['recipient']
        messages = Message.objects.get_messages(self.request.user, context['recipient'])
        messages.mark_as_read(self.request.user)
        context['paginator'], \
            context['page_obj'], \
            context['messages'], \
            context['is_paginated'] = self.paginate_queryset(messages)
        return context

    def get_success_url(self):
        return reverse('accounts:message-create', kwargs={'user_id': self.storage['recipient'].id})


"""====================================================== Chat ======================================================"""


class ChatList(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'accounts/chat/chat_list.html'
    context_object_name = 'chats'

    def get_queryset(self):
        return super().get_queryset().actual(self.request.user)


"""================================================== Announcement =================================================="""


class AnnouncementDetail(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'accounts/announcement/announcement_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = markdown(self.object.text)
        return context


class AnnouncementCreate(LoginAndPermissionRequiredMixin, CreateView):
    model = Announcement
    fields = ['group', 'title', 'text']
    template_name = 'accounts/announcement/announcement_form.html'
    permission_required = 'accounts.add_announcement'
    raise_exception = True

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AnnouncementUpdate(LoginAndPermissionRequiredMixin, UpdateView):
    model = Announcement
    fields = ['group', 'title', 'text']
    template_name = 'accounts/announcement/announcement_form.html'
    permission_required = 'accounts.change_announcement'
    raise_exception = True


class AnnouncementDelete(LoginAndPermissionRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('accounts:announcement-list')
    template_name = 'accounts/announcement/announcement_delete.html'
    permission_required = 'accounts.delete_announcement'
    raise_exception = True


class AnnouncementList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'accounts/announcement/announcement_list.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        if self.request.user.has_perm('contests.add_problem'):
            return super().get_queryset().all()
        else:
            return super().get_queryset().filter(group__in=self.request.user.groups.all())
