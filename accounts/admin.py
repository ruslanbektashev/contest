from django.contrib import admin
from django.contrib.auth.models import Permission

from accounts.models import Account, Activity, Comment, Message, Chat, Announcement


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'level', 'admission_year')
    list_filter = ('level', 'admission_year')
    search_fields = ('user__last_name', 'user__first_name')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Детали', {
            'fields': ('level', 'type', 'admission_year', 'enrolled', 'graduated')
        }),
        ('Даты', {
            'fields': ('date_updated',)
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
    list_display = ('__str__', 'is_deleted', 'date_created')
    list_editable = ('is_deleted',)
    search_fields = ('author__last_name', 'author__first_name')
    fieldsets = (
        ('Порядок', {
            'fields': ('thread_id', 'parent_id', 'level', 'order')
        }),
        ('Объект', {
            'fields': ('object_type', 'object_id')
        }),
        ('Ссылки', {
            'fields': ('author',)
        }),
        ('Детали', {
            'fields': ('text', 'is_deleted')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('date_created',)


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
