from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
