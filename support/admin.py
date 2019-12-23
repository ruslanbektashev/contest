from django.contrib import admin

from .models import FAQ
from .models import Report


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('owner', 'question', 'is_published')
    list_editable = ('is_published',)
    fieldsets = (
        ('Пользователь', {
            'fields': ('owner',)
        }),
        ('Детали', {
            'fields': ('question', 'answer', 'is_published')
        }),
        ('Даты', {
            'fields': ('date_created', 'date_updated')
        })
    )


admin.site.register(Report)
