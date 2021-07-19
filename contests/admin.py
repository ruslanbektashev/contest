from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from contests.forms import CourseForm
from contests.models import (Assignment, Attachment, Contest, Course, Credit, Event, Execution, FNTest, IOTest, Lecture,
                             Option, Problem, Submission, SubmissionPattern, Tag, UTTest)


class AttachmentInline(GenericStackedInline):
    model = Attachment
    extra = 1
    ct_field = 'object_type'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_updated', 'date_created')
    form = CourseForm
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'leaders', 'faculty')
        }),
        ('Детали', {
            'fields': ('title_official', 'title_unofficial', 'description', 'level')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'score', 'date_updated', 'date_created')
    list_editable = ('score',)
    list_filter = ('course__level',)
    list_select_related = ('user__account',)
    search_fields = ('course__title',)
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'user', 'course')
        }),
        ('Детали', {
            'fields': ('score',)
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')

    def name(self, instance):
        return instance.user.account


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_updated', 'date_created')
    list_filter = ('course__level',)
    search_fields = ('title',)
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'course')
        }),
        ('Детали', {
            'fields': ('title', 'description')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_updated', 'date_created')
    list_filter = ('course__level',)
    search_fields = ('title',)
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'course')
        }),
        ('Детали', {
            'fields': ('title', 'description', 'number')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


class IOTestInline(admin.StackedInline):
    model = IOTest
    extra = 1


class UTTestInline(admin.StackedInline):
    model = UTTest
    extra = 1
    inlines = [AttachmentInline]


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'number',
        'language',
        'compile_args',
        'launch_args',
        'time_limit',
        'memory_limit',
        'is_testable',
        'date_updated',
        'date_created'
    )
    list_editable = ('number', 'language', 'compile_args', 'launch_args', 'time_limit', 'memory_limit', 'is_testable',)
    list_filter = ('contest__course__level',)
    search_fields = ('title',)
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'contest')
        }),
        ('Детали', {
            'fields': (
                'title',
                'number',
                'description',
                'difficulty',
                'language',
                'compile_args',
                'launch_args',
                'time_limit',
                'memory_limit',
                'is_testable'
            )
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')
    inlines = [AttachmentInline, IOTestInline, UTTestInline]


@admin.register(SubmissionPattern)
class SubmissionPatternAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'problems')
        }),
        ('Детали', {
            'fields': ('title', 'description', 'pattern')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


@admin.register(FNTest)
class FNTestAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'problems')
        }),
        ('Детали', {
            'fields': ('title', 'handler')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'score', 'date_updated', 'date_created')
    list_filter = ('problem__contest__course__level',)
    search_fields = ('user__last_name', 'user__first_name', 'problem__title')
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'user', 'problem')
        }),
        ('Детали', {
            'fields': ('score', 'score_max', 'submission_limit', 'remark')
        }),
        ('Даты', {
            'fields': ('date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'status', 'task_id', 'date_created')
    list_filter = ('problem__contest__course__level', 'status')
    search_fields = ('owner__last_name', 'owner__first_name', 'problem__title')
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'problem', 'assignment')
        }),
        ('Детали', {
            'fields': ('status', 'score', 'task_id', 'footprint')
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('assignment', 'date_created')
    inlines = [AttachmentInline]


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'test_is_passed', 'date_created')
    list_filter = ('submission__problem__contest__course__level',)
    search_fields = ('submission__problem__title',)
    fieldsets = (
        ('Ссылки', {
            'fields': ('submission',)
        }),
        ('Тест', {
            'fields': ('test_type', 'test_id')
        }),
        ('Детали', {
            'fields': (
                'compilation_time',
                'compilation_command',
                'compilation_stdout',
                'compilation_stderr',
                'execution_memory',
                'execution_time',
                'execution_command',
                'execution_stdout',
                'execution_stderr',
                'execution_returncode',
                'test_is_passed',
                'test_input',
                'test_output',
                'test_output_correct',
                'test_summary',
                'exception',
            )
        }),
        ('Даты', {
            'fields': ('date_created',)
        })
    )
    readonly_fields = ('submission', 'date_created')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fieldsets = (
        ('Объект', {
            'fields': ('object_type', 'object_id')
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_start', 'date_end', 'date_updated', 'date_created')
    list_filter = ('type',)
    search_fields = ('title',)
    fieldsets = (
        ('Ссылки', {
            'fields': ('owner', 'tutor')
        }),
        ('Детали', {
            'fields': ('title', 'type', 'place', 'tags')
        }),
        ('Даты', {
            'fields': ('date_start', 'date_end', 'date_updated', 'date_created')
        })
    )
    readonly_fields = ('date_updated', 'date_created')


admin.site.register(Option)
