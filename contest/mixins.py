from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


class LoginRedirectMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        return super().dispatch(request, *args, **kwargs)


class LoginRedirectPermissionRequiredMixin(LoginRedirectMixin, PermissionRequiredMixin):
    raise_exception = True


class OwnershipOrPermissionRequiredMixin(PermissionRequiredMixin):
    def has_ownership(self):
        self.object = self.get_object()
        return self.object.owner.pk == self.request.user.pk

    def has_permission(self):
        return super().has_permission() or self.has_ownership()


class LoginRedirectOwnershipOrPermissionRequiredMixin(LoginRedirectMixin, OwnershipOrPermissionRequiredMixin):
    raise_exception = True


class PaginatorMixin:
    page_kwarg = 'page'
    paginate_by = None

    def paginate_queryset(self, queryset, page_size=None):
        page_size = page_size or self.paginate_by
        if page_size:
            paginator = Paginator(queryset, page_size)
            page_kwarg = self.page_kwarg
            page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()
        else:
            return None, None, queryset, False

    def get_context_data(self, **kwargs):
        kwargs.update(focus_page=self.page_kwarg in self.request.GET)
        return super().get_context_data(**kwargs)
