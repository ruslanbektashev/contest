import re
from html.entities import name2codepoint
from html.parser import HTMLParser

from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Account, Announcement, Comment
from accounts.templatetags.markdown import markdown


class AccountPartialForm(forms.ModelForm):
    email = forms.EmailField(label="e-mail", required=False)

    class Meta:
        model = Account
        fields = []

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance is not None:
            initial = {
                'email': instance.user.email
            }
            if 'initial' in kwargs:
                kwargs['initial'].update(initial)
            else:
                kwargs.update(initial=initial)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        super().save(commit)
        self.instance.user.email = self.cleaned_data['email']
        self.instance.user.save()
        return self.instance


class AccountForm(AccountPartialForm):
    first_name = forms.CharField(max_length=30, label="Имя")
    last_name = forms.CharField(max_length=150, label="Фамилия")
    is_active = forms.BooleanField(required=False, label="Активен")

    class Meta:
        model = Account
        fields = ['patronymic', 'faculty', 'department', 'position', 'degree', 'record_book_id', 'image', 'level',
                  'group', 'subgroup', 'type', 'admission_year', 'enrolled', 'graduated']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance is not None:
            initial = {
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'is_active': instance.user.is_active
            }
            if 'initial' in kwargs:
                kwargs['initial'].update(initial)
            else:
                kwargs.update(initial=initial)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        super(AccountPartialForm, self).save(commit)
        for field_name in ['email', 'first_name', 'last_name', 'is_active']:
            if field_name in self.changed_data:
                setattr(self.instance.user, field_name, self.cleaned_data[field_name])
        self.instance.user.save()
        return self.instance


class StudentForm(AccountForm):
    class Meta:
        model = Account
        fields = ['patronymic', 'faculty', 'record_book_id', 'level', 'group', 'subgroup', 'admission_year', 'enrolled',
                  'graduated']


class StaffForm(AccountForm):
    class Meta:
        model = Account
        fields = ['patronymic', 'faculty', 'department', 'position', 'degree', 'type']


class AccountListForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.students.none(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, queryset, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(queryset, list):
            self.fields['accounts'] = queryset
        else:
            self.fields['accounts'].queryset = queryset


class AccountSetForm(forms.ModelForm):
    names = forms.CharField(widget=forms.Textarea, label="Список")

    class Meta:
        model = Account
        fields = ['faculty', 'level', 'type', 'admission_year']

    def __init__(self, faculty, level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].initial = faculty
        self.fields['level'].initial = level
        self.fields['admission_year'].initial = timezone.now().year - (level // 2)

    def clean_faculty(self):
        faculty = self.cleaned_data['faculty']
        if faculty.is_interfaculty:
            raise ValidationError("В выбранный факультет нельзя добавить студентов", code='invalid_faculty')
        return faculty

    def clean_names(self):
        names = sorted(self.cleaned_data['names'].split('\r\n'))
        cleaned_names = []
        for name in names:
            initials = name.split()
            if len(initials) < 2:
                raise ValidationError("Неверный формат списка инициалов: {}. "
                                      "Фамилия и Имя должны присутствовать в каждой строке списка".format(name),
                                      code='wrong_format')
            length = min(len(initials), 4)
            for i in range(length):
                if not re.match(r'^[а-яА-ЯёЁ-]*$', initials[i]):
                    raise ValidationError("Недопустимый инициал: {}. "
                                          "Фамилия, Имя и Отчество должны состоять из букв русского алфавита "
                                          "и символов тире \"-\"".format(initials[i]), code='wrong_character')
            cleaned_names.append(initials)
        return cleaned_names


class MarkdownValidationParser(HTMLParser):
    def error(self, message):
        raise ValidationError(message, code='text_markdown_validation_error')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.safe_tags = ['p', 'em', 'strong', 'hr', 'ol', 'ul', 'li', 'a', 'blockquote', 'code', 'br', 'pre', 'h1',
                          'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
        self.safe_attrs = ['href', 'alt', 'src', 'class']

    def handle_startendtag(self, tag, attrs):
        if tag not in self.safe_tags:
            self.error("Использование тэга {} запрещено.".format(tag))
        for attr, value in attrs:
            if attr not in self.safe_attrs:
                self.error("Найден недопустимый атрибут {} тэга {}.".format(attr, tag))

    def handle_starttag(self, tag, attrs):
        if tag not in self.safe_tags:
            self.error("Использование тэга {} запрещено.".format(tag))
        for attr, value in attrs:
            if attr not in self.safe_attrs:
                self.error("Обнаружен недопустимый атрибут {} тэга {}.".format(attr, tag))

    def handle_endtag(self, tag):
        if tag not in self.safe_tags:
            self.error("Использование тэга {} запрещено.".format(tag))

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        self.error("Обнаружен недопустимый символ {}.".format(c))

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        self.error("Обнаружен недопустимый символ {}.".format(c))

    def handle_data(self, data):
        pass

    def handle_comment(self, data):
        self.error("Использование тэга comment запрещено.")

    def handle_decl(self, data):
        self.error("Использование определений запрещено.")

    def handle_pi(self, data):
        self.error("Использование инструкций запрещено.")

    def unknown_decl(self, data):
        self.error("Использование определений запрещено.")


class CommentForm(forms.ModelForm):
    text = forms.CharField(strip=False, widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ('parent_id', 'object_type', 'object_id', 'text')
        widgets = {'parent_id': forms.HiddenInput, 'object_type': forms.HiddenInput, 'object_id': forms.HiddenInput}

    def clean_text(self):
        parser = MarkdownValidationParser()
        parser.feed(markdown(self.cleaned_data['text']))
        return self.cleaned_data['text']

    def clean(self):
        parent_id = self.cleaned_data['parent_id']
        if parent_id and not Comment.objects.actual().filter(id=parent_id).exists():
            raise ValidationError("Нить комментирования отсутствует.", code='no_parent')
        return self.cleaned_data


class AnnouncementForm(forms.ModelForm):
    group = forms.ModelChoiceField(Group.objects.all(), empty_label="Для всех")

    class Meta:
        model = Announcement
        fields = ['group', 'title', 'text', 'actual']

    def clean_actual(self):
        actual = self.cleaned_data['actual']
        if actual is not None and actual < timezone.localdate():
            raise ValidationError("Укажите дату в будущем.", code='invalid_actual')
        return actual
