from django.db import models
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, UpdateView


class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super().update(soft_deleted=self.model.deleted_objects.get_deletion_id())

    def hard_delete(self):
        return super().delete()


class SoftDeletionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(soft_deleted=0)


class SoftDeletedQuerySet(models.QuerySet):
    def restore(self):
        return super().update(soft_deleted=0)

    def hard_delete(self):
        return super().delete()


class SoftDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(soft_deleted=0)

    def get_deletion_id(self):
        return (self.get_queryset().aggregate(models.Max('soft_deleted')).get('soft_deleted__max') or 0) + 1


class SoftDeletionModel(models.Model):
    soft_deleted = models.PositiveIntegerField(default=0, blank=True, verbose_name="В корзине")

    objects = SoftDeletionManager.from_queryset(SoftDeletionQuerySet)()
    deleted_objects = SoftDeletedManager.from_queryset(SoftDeletedQuerySet)()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.soft_deleted = self.__class__.deleted_objects.get_deletion_id()
        self.save()

    def hard_delete(self):
        return super().delete()


class SoftDeletionUpdateView(UpdateView):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.GET.get('action', None) == 'restore':
            form.instance.soft_deleted = 0
        return form

    def get_queryset(self):
        return self.model.all_objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = self.request.GET.get('action', None)
        return context


class SoftDeletionDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        if request.GET.get('action', None) == 'delete_permanently':
            self.object = self.get_object()
            success_url = self.get_success_url()
            self.object.hard_delete()
            return HttpResponseRedirect(success_url)
        else:
            return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.all_objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = self.request.GET.get('action', None)
        return context
