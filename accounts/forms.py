from html.entities import name2codepoint
from html.parser import HTMLParser

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Account, Activity, Comment
from accounts.templatetags.markdown import markdown
from accounts.widgets import CommentWidget


class AccountPartialForm(forms.ModelForm):
    email = forms.EmailField(label="e-mail", required=False)

    class Meta:
        model = Account
        fields = []

    def save(self, commit=True):
        super().save(commit)
        self.instance.user.email = self.cleaned_data['email']
        self.instance.user.save()
        return self.instance


class AccountForm(AccountPartialForm):
    first_name = forms.CharField(max_length=30, label="Имя")
    last_name = forms.CharField(max_length=150, label="Фамилия")

    class Meta:
        model = Account
        fields = ['patronymic', 'department', 'position', 'degree', 'image', 'level', 'type', 'admission_year',
                  'enrolled', 'graduated']

    def save(self, commit=True):
        super(AccountPartialForm, self).save(commit)
        for field_name in ['email', 'first_name', 'last_name']:
            if field_name in self.changed_data:
                setattr(self.instance.user, field_name, self.cleaned_data[field_name])
        self.instance.user.save()
        return self.instance


class AccountListForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.students.all(),
                                              widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        account_type = kwargs.pop('type', None)
        super().__init__(*args, **kwargs)
        if account_type is not None and account_type > 1:
            self.fields['accounts'].queryset = Account.staff.filter(type=account_type)


class AccountSetForm(forms.ModelForm):
    names = forms.CharField(widget=forms.Textarea, label="Список")

    class Meta:
        model = Account
        fields = ['level', 'type', 'admission_year']

    def __init__(self, level, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level'].initial = level
        self.fields['admission_year'].initial = timezone.now().year - (level // 2)

    def clean_names(self):
        names = sorted(self.cleaned_data['names'].split('\r\n'))
        cleaned_names = []
        for name in names:
            name = name.split()
            if len(name) < 2:
                raise ValidationError('Неверный формат списка имен', code='wrong_format')
            for i in range(2):
                if not name[i].isalpha():
                    raise ValidationError('Фамилия и Имя должны состоять только из букв', code='not_a_letter')
                name[i].lower().capitalize()
            cleaned_names.append(name)
        return cleaned_names


class ActivityMarkForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(queryset=Activity.objects.all())


class MarkdownValidationParser(HTMLParser):
    def error(self, message):
        raise ValidationError("Разметка временно недоступна. Используйте только текст.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stack = []
        self.safe_tags = ['p', 'code', 'pre']

    def handle_startendtag(self, tag, attrs):
        self.error('startend tag')

    def handle_starttag(self, tag, attrs):
        if attrs:
            self.error('tag attrs')
        if tag not in self.safe_tags:
            self.error('unsafe tag')
        self.stack.append(tag)
        if len(self.stack) > 1:
            self.error('nested tag: %s' % tag)

    def handle_endtag(self, tag):
        if tag not in self.safe_tags:
            self.error('unsafe tag')
        if not self.stack:
            self.error('unexpected endtag: %s' % tag)
        if self.stack.pop() != tag:
            self.error('unclosed tag')

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        self.error('char %s' % c)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        self.error('entity %s' % c)

    def handle_data(self, data):
        pass

    def handle_comment(self, data):
        self.error('comment')

    def handle_decl(self, data):
        self.error('decl %s' % data)

    def handle_pi(self, data):
        self.error('pi %s' % data)

    def unknown_decl(self, data):
        self.error('unknown decl %s' % data)


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=CommentWidget())

    class Meta:
        model = Comment
        fields = ('parent_id', 'object_type', 'object_id', 'text')
        widgets = {
            'parent_id': forms.HiddenInput,
            'object_type': forms.HiddenInput,
            'object_id': forms.HiddenInput
        }

    def clean_text(self):
        parser = MarkdownValidationParser()
        parser.feed(markdown(self.cleaned_data['text']))
        return self.cleaned_data['text']

    def clean(self):
        parent_id = self.cleaned_data['parent_id']
        if parent_id and not Comment.objects.actual().filter(id=parent_id).exists():
            raise ValidationError('Нить комментирования отсутствует', code='no_parent')
        return self.cleaned_data
