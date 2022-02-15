import os

from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils import timezone

from schedule.models import Schedule, ScheduleAttachment


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['date_from', 'date_to']

    def clean_date_from(self):
        date_from = self.cleaned_data.get('date_from')
        current_year = timezone.now().year
        if (date_from.year < current_year) or (date_from.year > current_year + 1):
            raise ValidationError("Расписание можно добавить только для текущего %(valid_year)s года",
                                  code='invalid_year', params={'valid_year': current_year})
        return date_from

    def clean_date_to(self):
        date_to = self.cleaned_data.get('date_to')

        return date_to

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        if date_from and date_to:
            if date_from >= date_to:
                self.add_error('date_from', ValidationError("Выбран противоречивый интервал", code='invalid_interval'))
            if date_from + timedelta(days=31) < date_to:
                self.add_error('date_from', ValidationError("Выбран слишком большой интервал", code='invalid_interval'))
        return self.cleaned_data


class ScheduleAttachmentForm(forms.ModelForm):
    FILE_SIZE_LIMIT = 10 * 1024 * 1024
    FILE_ALLOWED_NAMES = tuple()
    FILE_ALLOWED_EXTENSIONS = ['.htm', '.pdf']

    class Meta:
        model = ScheduleAttachment
        fields = ['name', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file.size > self.FILE_SIZE_LIMIT:
            raise ValidationError("Размер файла не должен превышать %(files_size_limit)s",
                                  code='large_file', params={'files_size_limit': filesizeformat(self.FILE_SIZE_LIMIT)})
        filename = os.path.splitext(file.name)
        if not filename[1].lower() in self.FILE_ALLOWED_EXTENSIONS:
            if not filename[0].startswith(self.FILE_ALLOWED_NAMES):
                raise ValidationError("Допустимы только файлы с расширениями: %(files_allowed_extensions)s",
                                      code='invalid_extension',
                                      params={'files_allowed_extensions': ', '.join(self.FILE_ALLOWED_EXTENSIONS)})
        return file


class ScheduleAttachmentBaseFormSet(forms.BaseInlineFormSet):
    def full_clean(self):
        super().full_clean()
        for error in self._non_form_errors.as_data():
            if error.code in ('too_many_forms', 'too_few_forms'):
                error.message = "Необходимо выбрать файлы с расписанием для всех %d групп." % self.max_num
