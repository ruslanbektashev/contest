from django.contrib import admin

from support.models import Question, Report


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'question', 'is_published')
    list_editable = ('is_published',)
    fieldsets = (
        ('Пользователи', {
            'fields': ('owner', 'addressee')
        }),
        ('Детали', {
            'fields': ('question', 'answer', 'is_published', 'redirect_comment')
        }),
        ('Даты', {
            'fields': ('date_created', 'date_updated')
        })
    )
    readonly_fields = ('date_created', 'date_updated')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title')
    fieldsets = (
        ('Пользователь', {
            'fields': ('owner',)
        }),
        ('Детали', {
            'fields': ('title', 'text', 'page_url')
        }),
        ('Даты', {
            'fields': ('date_created', 'date_updated')
        })
    )
    readonly_fields = ('date_created', 'date_updated')
