from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission

from accounts.models import Account, Action, Announcement, Comment, Faculty, Notification


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user_full_name', 'get_edited_object', 'action_time')

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = "Пользователь"

    def get_edited_object(self, obj):
        return obj.get_edited_object()
    get_edited_object.short_description = "Измененный объект"


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fields = ('name', 'short_name', 'group_name', 'group_prefix')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'date_joined', 'last_login', 'faculty', 'level', 'admission_year')
    list_filter = ('department', 'faculty', 'level', 'type', 'admission_year', 'enrolled', 'graduated')
    search_fields = ('user__last_name', 'user__first_name')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Детали', {
            'fields': ('patronymic', 'department', 'position', 'degree', 'image', 'faculty', 'level', 'type',
                       'admission_year', 'enrolled', 'graduated', 'record_book_id')
        }),
        ('Даты', {
            'fields': ('date_updated',)
        }),
        ('Другое', {
            'fields': ('comments_read',)
        })
    )
    readonly_fields = ('date_updated',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_full_name', 'object_type', 'object', 'short_text', 'is_deleted', 'date_created')
    list_editable = ('is_deleted',)
    list_select_related = ('author', 'object_type', 'object')
    search_fields = ('author__last_name', 'author__first_name')
    fieldsets = (
        ('Порядок', {
            'fields': (('thread_id', 'parent_id', 'level', 'order'),)
        }),
        ('Объект', {
            'fields': (('object_type', 'object_id', 'object'),)
        }),
        ('Ссылки', {
            'fields': ('author_full_name',)
        }),
        ('Детали', {
            'fields': ('text', 'is_deleted')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('date_created', 'object', 'author_full_name')

    def author_full_name(self, obj):
        return obj.author.get_full_name()
    author_full_name.short_description = "Автор"

    def short_text(self, obj):
        return obj.text[:60] + (obj.text[60:] and "...")
    short_text.short_description = "Текст комментария"


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_updated', 'date_created')
    search_fields = ('title', 'text')
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'group')
        }),
        ('Детали', {
            'fields': ('title', 'text')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_read', 'is_deleted', 'date_created')
    list_editable = ('is_read', 'is_deleted')
    search_fields = ('action', 'recipient__last_name', 'recipient__first_name')
    fieldsets = (
        ('Субъект', {
            'fields': ('subject_type', 'subject_id')
        }),
        ('Объект', {
            'fields': ('object_type', 'object_id')
        }),
        ('Связь', {
            'fields': ('reference_type', 'reference_id', 'relation')
        }),
        ('Ссылки', {
            'fields': ('recipient',)
        }),
        ('Детали', {
            'fields': ('action', 'is_read', 'is_deleted')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user_full_name', 'date_created')
    list_filter = ('action_type',)
    fieldsets = (
        ('Мета', {
            'fields': ('user', 'action_type')
        }),
        ('Подробности', {
            'fields': ('details', 'get_details')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('get_details', 'date_created')

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = "Пользователь"

    def get_details(self, obj):
        return obj.get_details()
    get_details.short_description = "Расшифровка"
