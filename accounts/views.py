import json

from markdown import markdown

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView, FormView, TemplateView
from django.views.generic.edit import BaseUpdateView
from django.views.generic.list import BaseListView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from accounts.templatetags.comments import get_comment_query_string
from contest.mixins import (LoginRedirectPermissionRequiredMixin, LoginRedirectOwnershipOrPermissionRequiredMixin,
                            PaginatorMixin)
from accounts.forms import (AccountPartialForm, AccountForm, AccountListForm, AccountSetForm, ActivityMarkForm,
                            CommentForm, ManageSubscriptionsForm)
from accounts.models import Account, Activity, Comment, Faculty, Message, Chat, Announcement, Subscription
from contests.models import Course, Submission

"""==================================================== Account ====================================================="""


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
def mark_activities_as_read(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'status': 'bad_request'})
    unread_activities_ids = data.get('unread_activities_ids', None)
    if unread_activities_ids:
        unread_activities = Activity.objects.filter(id__in=unread_activities_ids, recipient=request.user)
        unread_activities.mark_as_read()
    return JsonResponse({'status': 'ok'})


class AccountDetail(LoginRedirectOwnershipOrPermissionRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account/account_detail.html'
    permission_required = 'accounts.view_account'

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = (self.object.user.assignment_set
                                  .select_related('problem', 'problem__contest', 'problem__contest__course')
                                  .order_by('-problem__contest__course', '-problem__contest', '-date_created'))
        context['credits'] = self.object.user.credit_set.select_related('course')
        return context


class AccountCreateSet(LoginRedirectPermissionRequiredMixin, FormView):
    form_class = AccountSetForm
    template_name = 'accounts/account/account_set_form.html'
    permission_required = 'accounts.add_account'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        faculty_id = int(self.request.GET.get('faculty_id') or request.user.account.faculty_id)
        self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
        self.storage['level'] = int(self.request.GET.get('level') or 1)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['faculty'] = self.storage['faculty']
        kwargs['level'] = self.storage['level']
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
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
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty'] = self.storage['faculty']
        return context

    def get_success_url(self):
        return reverse('accounts:account-credentials') + "?faculty_id={}".format(self.storage['faculty'].id)


class AccountUpdate(LoginRedirectOwnershipOrPermissionRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account/account_form.html'
    permission_required = 'account.change_account'

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):  # self.object may be set in LoginRedirectOwnershipOrPermissionRequiredMixin
            self.object = self.get_object()
        return super(BaseUpdateView, self).post(request, *args, **kwargs)

    def get_form_class(self):
        if self.request.user.has_perm('accounts.change_account'):
            return self.form_class
        else:
            return AccountPartialForm

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.has_perm('accounts.change_account'):
            initial['first_name'] = self.object.first_name
            initial['last_name'] = self.object.last_name
        initial['email'] = self.object.email
        return initial


class AccountFormList(LoginRedirectPermissionRequiredMixin, BaseListView, FormView):
    model = Account
    form_class = AccountListForm
    template_name = 'accounts/account/account_list.html'
    context_object_name = 'accounts'
    permission_required = 'accounts.change_account'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        faculty_id = int(self.request.GET.get('faculty_id') or request.user.account.faculty_id)
        self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
        self.storage['level'] = int(self.request.GET.get('level') or 1)
        self.storage['type'] = int(self.request.GET.get('type') or 1)
        enrolled, graduated = self.request.GET.get('enrolled'), self.request.GET.get('graduated')
        if enrolled is not None and enrolled == '0':
            self.storage['enrolled'] = False
            self.storage['graduated'] = False
        if graduated is not None and graduated == '1':
            self.storage['enrolled'] = False
            self.storage['graduated'] = True
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            action = request.POST.get('action')
            accounts = form.cleaned_data['accounts']
            if action == 'reset_password':
                self.request.session['credentials'] = accounts.reset_password()
                return HttpResponseRedirect(reverse('accounts:account-credentials'))
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

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def get_queryset(self):
        if self.storage['type'] > 1:
            queryset = Account.staff.filter(type=self.storage['type'])
        else:
            queryset = Account.students.all()
            if 'enrolled' in self.storage and 'graduated' in self.storage:
                queryset = queryset.filter(enrolled=self.storage['enrolled'], graduated=self.storage['graduated'])
            else:
                queryset = queryset.enrolled().filter(level=self.storage['level'])
        return queryset.filter(faculty=self.storage['faculty'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = Account.LEVEL_CHOICES
        context.update(self.storage)
        return context

    def get_success_url(self):
        return self.request.get_full_path()


class AccountCredentials(LoginRedirectPermissionRequiredMixin, TemplateView):
    template_name = 'accounts/account/account_credentials.html'
    permission_required = 'accounts.add_account'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        self.storage['credentials'] = self.request.session.pop('credentials', None)
        faculty_id = int(self.request.GET.get('faculty_id') or request.user.account.faculty_id)
        self.storage['faculty'] = get_object_or_404(Faculty, id=faculty_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['credentials'] = self.storage.pop('credentials')
        context['faculty'] = self.storage['faculty']
        return context


"""================================================== Subscription =================================================="""


class SubscriptionCreate(CreateView):
    model = Subscription
    permission_required = 'account.add_subscription'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['previous_url'] = self.request.GET.get('previous_url', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = Subscription(
            object=ContentType.objects.get(
                app_label='contests',
                model=kwargs.pop('object_model')
            ).get_object_for_this_type(id=kwargs.pop('object_id')),
            user=self.request.user
        )
        self.object.save()

        comment_type = ContentType.objects.get(model='comment')
        if not self.request.user.subscription_set.filter(object_type=comment_type).exists():
            comment_subscription = Subscription(object_type=comment_type, user=self.request.user)
            comment_subscription.save()
        submission_type = ContentType.objects.get(model='submission')
        if not self.request.user.subscription_set.filter(object_type=submission_type).exists():
            submission_subscription = Subscription(object_type=submission_type, user=self.request.user)
            submission_subscription.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.storage['previous_url']


class SubscriptionDelete(DeleteView):
    model = Subscription
    permission_required = 'account.delete_subscription'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = dict()

    def dispatch(self, request, *args, **kwargs):
        self.storage['previous_url'] = self.request.GET.get('previous_url', '')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.subscription_set.filter(object_type=ContentType.objects.get(model='course')).count() == 1:
            comment_submission_types = ContentType.objects.filter(model__in=['comment', 'submission'])
            self.request.user.subscription_set.filter(object_type__in=comment_submission_types).delete()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.storage['previous_url']


class ManageSubscriptions(LoginRequiredMixin, FormView):
    form_class = ManageSubscriptionsForm
    template_name = 'accounts/activity/activity_settings.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['object_type'] = list(self.request.user.subscription_set.values_list('object_type', flat=True))
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_ids = self.request.user.subscription_set.filter(object_type=ContentType.objects.get(model='course')).values_list('object_id', flat=True)
        context['courses'] = Course.objects.filter(id__in=course_ids)
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = self.request.user
            choices = form.fields['object_type'].choices
            data = form.cleaned_data['object_type']
            
            user.subscription_set.filter(object_type__in=choices).exclude(object_type__in=data).delete()
            
            new_object_type_ids = set(map(int, data)) - set(user.subscription_set.values_list('object_type', flat=True))
            new_subscriptions = (Subscription(object_type=ContentType.objects.get(id=i), user=user) for i in new_object_type_ids)
            Subscription.objects.bulk_create(new_subscriptions)

            comment_submission_types = ContentType.objects.filter(model__in=['comment', 'submission'])
            if not user.subscription_set.filter(object_type__in=comment_submission_types).exists():
                user.subscription_set.filter(object_type=ContentType.objects.get(model='course')).delete()
            if user.subscription_set.filter(object_type__in=comment_submission_types).exists() and not user.subscription_set.filter(object_type=ContentType.objects.get(model='course')).exists():
                course_ids = Course.objects.all().values_list('id', flat=True)
                course_subscriptions = (Subscription(object_type=ContentType.objects.get(model='course'), object_id=course_id, user=user) for course_id in course_ids)
                Subscription.objects.bulk_create(course_subscriptions)

            return self.form_valid(form)
        return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('accounts:activity-settings')


"""==================================================== Activity ===================================================="""


class ActivityList(LoginRequiredMixin, PaginatorMixin, ListView):
    model = Activity
    template_name = 'accounts/activity/activity_list.html'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = super().get_queryset().filter(recipient=self.request.user).actual()
        context['paginator'], context['page_obj'], context['activities'], context['is_paginated'] = \
            self.paginate_queryset(activities)
        return context


class ActivityMark(LoginRequiredMixin, FormView):
    form_class = ActivityMarkForm
    http_method_names = ['post']
    template_name = 'accounts/activity/activity_list.html'

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


class CommentCreate(LoginRedirectPermissionRequiredMixin, CreateView):
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


class CommentUpdate(LoginRedirectOwnershipOrPermissionRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'accounts/comment/comment_update.html'
    permission_required = 'accounts.change_comment'

    def get_success_url(self):
        page = self.request.GET.get('page', '1')
        return self.object.object.get_discussion_url() + get_comment_query_string(page) + '#comment_' + str(self.object.pk)


class CommentDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Comment
    template_name = 'accounts/comment/comment_delete.html'
    permission_required = 'accounts.delete_comment'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.soft_delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        page = self.request.GET.get('page', '1')
        return self.object.object.get_discussion_url() + get_comment_query_string(page)


"""==================================================== Message ====================================================="""


class MessageCreate(LoginRedirectPermissionRequiredMixin, PaginatorMixin, CreateView):
    model = Message
    fields = ['text']
    template_name = 'accounts/message/message_form.html'
    permission_required = 'accounts.add_message'
    # TODO: set proper items-per-page
    paginate_by = 100

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = {}

    def dispatch(self, request, *args, **kwargs):
        self.storage['recipient'] = get_object_or_404(User, id=kwargs.pop('user_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.recipient = self.storage['recipient']
        response = super().form_valid(form)
        Chat.objects.update_or_create_chat(self.request.user, self.storage['recipient'], self.object)
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


class AnnouncementDetail(LoginRedirectPermissionRequiredMixin, DetailView):
    model = Announcement
    template_name = 'accounts/announcement/announcement_detail.html'
    permission_required = 'accounts.view_announcement'

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        Activity.objects.filter(recipient=request.user, object_type=ContentType.objects.get_for_model(object), object_id=object.id).mark_as_read()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = markdown(self.object.text)
        return context


class AnnouncementCreate(LoginRedirectPermissionRequiredMixin, CreateView):
    model = Announcement
    fields = ['group', 'title', 'text']
    template_name = 'accounts/announcement/announcement_form.html'
    permission_required = 'accounts.add_announcement'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AnnouncementUpdate(LoginRedirectPermissionRequiredMixin, UpdateView):
    model = Announcement
    fields = ['group', 'title', 'text']
    template_name = 'accounts/announcement/announcement_form.html'
    permission_required = 'accounts.change_announcement'


class AnnouncementDelete(LoginRedirectPermissionRequiredMixin, DeleteView):
    model = Announcement
    success_url = reverse_lazy('accounts:announcement-list')
    template_name = 'accounts/announcement/announcement_delete.html'
    permission_required = 'accounts.delete_announcement'


class AnnouncementList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'accounts/announcement/announcement_list.html'
    context_object_name = 'announcements'

    def get_queryset(self):
        if self.request.user.has_perm('contests.change_announcement'):
            return super().get_queryset().all()
        else:
            return super().get_queryset().filter(group__in=self.request.user.groups.all())
