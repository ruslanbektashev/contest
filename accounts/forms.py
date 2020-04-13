from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Account, Activity, Comment
from accounts.widgets import MyNewWidget


class AccountPartialForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail", required=False)

    class Meta:
        model = Account
        fields = []

    def save(self, commit=True):
        super().save(commit)
        self.instance.user.email = self.cleaned_data['email']
        self.instance.user.save()
        return self.instance


class AccountForm(AccountPartialForm):
    class Meta:
        model = Account
        fields = ['level', 'type', 'admission_year', 'enrolled', 'graduated']


class AccountListForm(forms.Form):
    accounts = forms.ModelMultipleChoiceField(queryset=Account.students.all(),
                                              widget=forms.CheckboxSelectMultiple)


class AccountSetForm(forms.ModelForm):
    names = forms.CharField(widget=forms.Textarea, label="Список")

    class Meta:
        model = Account
        fields = ['level', 'admission_year']

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
                raise ValidationError(
                    'Неверный формат списка имен',
                    code='wrong_format'
                )
            cleaned_names.append(name)
        return cleaned_names


class ActivityMarkForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(queryset=Activity.objects.all())


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=MyNewWidget())
    class Meta:
        model = Comment
        fields = ('parent_id', 'object_type', 'object_id', 'text')
        widgets = {
            'parent_id': forms.HiddenInput,
            'object_type': forms.HiddenInput,
            'object_id': forms.HiddenInput
        }
