from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
