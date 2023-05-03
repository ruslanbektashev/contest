from django import forms
from django.contrib.auth.models import User

from contests.forms import BootstrapSelect, UserChoiceField
from support.models import Question


class QuestionForm(forms.ModelForm):
    addressee = UserChoiceField(queryset=User.objects.none(), label="Адресат")

    class Meta:
        model = Question
        fields = ['addressee', 'question', 'answer', 'is_published', 'redirect_comment']

    def __init__(self, addressee_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['addressee'].queryset = addressee_queryset
        option_subtext_data = addressee_queryset.values_list('pk', 'account__faculty__short_name')
        option_subtext_data = {pk: faculty_short_name for pk, faculty_short_name in option_subtext_data}
        option_subtext_data[''] = ''
        option_attrs = {'data-subtext': option_subtext_data}
        self.fields['addressee'].widget = BootstrapSelect(choices=self.fields['addressee'].choices,
                                                          option_attrs=option_attrs)
