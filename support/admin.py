from django.contrib import admin

from support.models import Discussion, Question, Report,ReportForCourse


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
    readonly_fields = ('date_created', 'date_updated')


# @admin.register(ReportForCourse)
# class MyModelAdmin(admin.ModelAdmin):
#     list_display = ('owner', 'title') # поля, которые будут отображаться в списке объектов

# admin.site.register(ReportForCourse, MyModelAdmin)

admin.site.register(ReportForCourse)

# @admin.register(ReportForCourse)
# class ReportCourseAdmin(admin.ModelAdmin):
#     list_display = ('owner', 'title')
#     readonly_fields = ('date_created', 'date_updated')


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('owner', 'topic')
    fieldsets = (
        ('Пользователь', {
            'fields': ('owner',)
        }),
        ('Детали', {
            'fields': ('topic',)
        }),
        ('Даты', {
            'fields': ('date_created', 'date_updated')
        })
    )
    readonly_fields = ('date_created', 'date_updated')
