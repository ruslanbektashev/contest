from django.apps import apps
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404


class LoginRedirectMixin(AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        return super().dispatch(request, *args, **kwargs)


class OwnershipOrMixin:
    def has_ownership(self):
        raise NotImplementedError("OwnershipOrMixin: has_ownership method must be defined!")

    def has_permission(self):
        return self.has_ownership() or super().has_permission()


class LeadershipOrMixin:
    def has_leadership(self):
        raise NotImplementedError("LeadershipOrMixin: has_leadership method must be defined!")

    def has_permission(self):
        return self.has_leadership() or super().has_permission()


class PaginatorMixin:
    page_kwarg = 'page'
    paginate_by = None

    def get_queryset_for_paginator(self):
        raise NotImplementedError("PaginatorMixin: get_queryset_for_paginator method must be defined!")

    def get_paginate_by(self, queryset):
        if self.paginate_by is None:
            raise NotImplementedError("PaginatorMixin: paginate_by or get_paginate_by should be overriden!")
        return self.paginate_by

    def paginate_queryset(self, queryset, page_size, page_number=None):
        paginator = Paginator(queryset, page_size)
        if page_number is None:
            page_kwarg = self.page_kwarg
            page_number = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page_number)
        except ValueError:
            if page_number == 'last':
                page_number = paginator.num_pages
            else:
                page_number = 1
        try:
            return paginator.page(page_number)
        except InvalidPage:
            raise Http404("Страница не найдена")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset_for_paginator()
        page_size = self.get_paginate_by(queryset)
        context['page_obj'] = self.paginate_queryset(queryset, page_size)
        return context


class LogAdditionMixin:
    def form_valid(self, form):
        response = super().form_valid(form)
        action_model = apps.get_model('accounts.Action')
        action_model.objects.log_addition(self.request.user, form=form)
        return response


class LogChangeMixin:
    def form_valid(self, form):
        response = super().form_valid(form)
        action_model = apps.get_model('accounts.Action')
        action_model.objects.log_change(self.request.user, form=form)
        return response


class LogDeletionMixin:
    def delete(self, request, *args, **kwargs):
        action_model = apps.get_model('accounts.Action')
        action_model.objects.log_deletion(request.user, obj=self.get_object())
        return super().delete(request, *args, **kwargs)
