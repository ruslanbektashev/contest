from django.contrib import admin
from django.contrib.auth.models import Permission

from accounts.models import Account, Activity, Comment, Faculty, Message, Chat, Announcement, Subscription


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fields = ('name', 'short_name', 'group_name', 'group_prefix')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'faculty', 'level', 'admission_year')
    list_filter = ('department', 'faculty', 'level', 'type', 'admission_year', 'enrolled', 'graduated')
    filter_horizontal = ('comments_read',)
    search_fields = ('user__last_name', 'user__first_name')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Детали', {
            'fields': ('patronymic', 'department', 'position', 'degree', 'image', 'faculty', 'level', 'type', 'admission_year', 'enrolled', 'graduated', 'record_book_id')
        }),
        ('Даты', {
            'fields': ('date_updated',)
        }),
        ('Другое', {
            'fields': ('comments_read',)
        })
    )
    readonly_fields = ('date_updated',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_read', 'is_deleted', 'date_created')
    list_editable = ('is_read', 'is_deleted')
    list_filter = ('level',)
    search_fields = ('action', 'recipient__last_name', 'recipient__first_name')
    fieldsets = (
        ('Субъект', {
            'fields': ('subject_type', 'subject_id')
        }),
        ('Объект', {
            'fields': ('object_type', 'object_id')
        }),
        ('Связь', {
            'fields': ('reference_type', 'reference_id')
        }),
        ('Ссылки', {
            'fields': ('recipient',)
        }),
        ('Детали', {
            'fields': ('action', 'level', 'is_read', 'is_deleted')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_name', 'object_type', 'object', 'short_text', 'is_deleted', 'date_created')
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
            'fields': ('author_name',)
        }),
        ('Детали', {
            'fields': ('text', 'is_deleted')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('date_created', 'object', 'author_name')

    def author_name(self, obj):
        return obj.author.get_full_name()
    author_name.short_description = 'Автор'

    def short_text(self, obj):
        return obj.text[:60] + (obj.text[60:] and '...')
    short_text.short_description = 'Текст комментария'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_read', 'is_deleted', 'date_created')
    list_editable = ('is_read', 'is_deleted')
    search_fields = ('sender__last_name', 'sender__first_name', 'recipient__last_name', 'recipient__first_name')
    fieldsets = (
        ('Ссылки', {
            'fields': ('sender', 'recipient')
        }),
        ('Детали', {
            'fields': ('text', 'is_read', 'is_deleted')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('date_created',)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'latest_message')
    fieldsets = (
        ('Ссылки', {
            'fields': ('user_a', 'user_b')
        }),
        ('Детали', {
            'fields': ('latest_message',)
        }),
    )


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Объект', {
            'fields': ('object_type', 'object_id')
        }),
        ('Пользователь', {
            'fields': ('user',)
        }),
    )
