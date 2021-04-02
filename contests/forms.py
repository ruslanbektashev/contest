import os
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.widgets import SelectMultiple
from django.template.defaultfilters import filesizeformat

from accounts.models import Account
from contests.models import (Answer, Attachment, Course, Contest, Option, Problem, SubmissionPattern, TestMembership, UTTest, FNTest, Assignment, Submission, Event, Test, Question)


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} {}".format(obj.last_name, obj.first_name)


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{} {}".format(obj.last_name, obj.first_name)


class AccountSelectMultiple(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=(), option_attrs=None):
        super().__init__(attrs, choices)
        self.option_attrs = option_attrs

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        displays = dict(Account.LEVEL_CHOICES)
        if self.option_attrs is not None:
            for data_attr, values in self.option_attrs.items():
                option['attrs'][data_attr] = displays[values[option['value']]]
        return option


"""=================================================== Attachment ==================================================="""


class AttachmentForm(forms.ModelForm):
    FILES_MAX = 10
    FILES_MIN = 0
    FILES_SIZE_LIMIT = 1024 * 1024
    FILES_ALLOWED_NAMES = tuple()
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt']

    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False, label="Файлы")

    class Meta:
        abstract = True
        model = Attachment
        fields = []

    def clean_files(self):
        if not self.files and self.FILES_MIN == 0:
            return self.files
        elif not self.files:
            raise ValidationError(
                'Выберите хотя бы %(files_min)i файл для посылки',
                code='not_enough_files',
                params={'files_min': self.FILES_MIN}
            )
        files = self.files.getlist('files')
        if len(files) > self.FILES_MAX:
            raise ValidationError(
                'Слишком много файлов. Допустимо посылать не более %(files_max)i',
                code='too_many_files',
                params={'files_max': self.FILES_MAX}
            )
        else:
            for file in files:
                if file.size > self.FILES_SIZE_LIMIT:
                    raise ValidationError(
                        'Размер каждого файла не должен превышать %(files_size_limit)s',
                        code='large_file',
                        params={'files_size_limit': filesizeformat(self.FILES_SIZE_LIMIT)}
                    )
                filename = os.path.splitext(file.name)
                if not filename[1].lower() in self.FILES_ALLOWED_EXTENSIONS:
                    if not filename[0].startswith(self.FILES_ALLOWED_NAMES):
                        raise ValidationError(
                            'Допустимы только файлы с расширениями: %(files_allowed_extensions)s',
                            code='invalid_extension',
                            params={'files_allowed_extensions': ', '.join(self.FILES_ALLOWED_EXTENSIONS)}
                        )
        return files

    def save(self, commit=True):
        obj = super().save()
        if self.files:
            files = self.files.getlist('files')
            instance_type = ContentType.objects.get_for_model(obj)
            new_attachments = []
            for file in files:
                new_attachment = Attachment(owner=obj.owner,
                                            object_type=instance_type,
                                            object_id=obj.id,
                                            file=file)
                new_attachments.append(new_attachment)
            Attachment.objects.bulk_create(new_attachments)
        return obj


"""===================================================== Course ====================================================="""


class CourseForm(forms.ModelForm):
    leaders = UserMultipleChoiceField(queryset=User.objects.none(), label="Ведущие преподаватели")

    class Meta:
        model = Course
        fields = ['leaders', 'title', 'description', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leaders'].queryset = User.objects.filter(account__type=3)


"""===================================================== Credit ====================================================="""


class CreditSetForm(forms.Form):
    runner_ups = UserMultipleChoiceField(queryset=Account.objects.none(), required=True, label="Выберите студентов")

    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        runner_ups = Account.students.enrolled().allowed(course).filter(credit_id=None)
        self.fields['runner_ups'].queryset = runner_ups.order_by('-level', 'user__last_name', 'user__first_name')
        self.fields['runner_ups'].initial = runner_ups.filter(level__in=[course.level - 1, course.level])
        option_attrs = {'data-subtext': dict(self.fields['runner_ups'].queryset.values_list('pk', 'level'))}
        option_attrs['data-subtext'][''] = ''
        self.fields['runner_ups'].widget = AccountSelectMultiple(choices=self.fields['runner_ups'].choices,
                                                                 option_attrs=option_attrs)


"""==================================================== Contest ====================================================="""


class ContestForm(AttachmentForm):
    FILES_SIZE_LIMIT = 10 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.doc', '.docx', '.ppt', '.pptx', '.pdf']

    class Meta:
        model = Contest
        fields = ['course', 'title', 'description', 'number']
        widgets = {'course': forms.HiddenInput}


"""==================================================== Problem ====================================================="""


class ProblemForm(AttachmentForm):
    FILES_SIZE_LIMIT = 10 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.doc', '.docx', '.ppt', '.pptx', '.pdf']

    class Meta:
        model = Problem
        fields = ['contest', 'title', 'description', 'number', 'difficulty', 'language', 'compile_args', 'launch_args',
                  'time_limit', 'memory_limit', 'is_testable']
        widgets = {'contest': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_limit'].append_text = "секунд"
        self.fields['memory_limit'].append_text = "КБайт"


class ProblemRollbackResultsForm(forms.Form):
    submissions = forms.ModelMultipleChoiceField(Submission.objects.none(), label="Посылки")

    def __init__(self, *args, problem_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submissions'].queryset = Submission.objects.to_rollback(problem_id)


"""=============================================== SubmissionPattern ================================================"""


class SubmissionPatternForm(forms.ModelForm):
    class Meta:
        model = SubmissionPattern
        fields = ['problems', 'title', 'description', 'pattern']

    def __init__(self, *args, problem=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['problems'].choices = grouped_problems(None, problem.contest, multiple=True)
        self.fields['problems'].initial = (problem,)


"""===================================================== UTTest ====================================================="""


class UTTestForm(AttachmentForm):
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp']

    class Meta:
        model = UTTest
        fields = ['title', 'compile_args', 'compile_args_override', 'launch_args', 'launch_args_override']


"""===================================================== FNTest ====================================================="""


class FNTestForm(forms.ModelForm):
    class Meta:
        model = FNTest
        fields = ['problems', 'title', 'handler']

    def __init__(self, *args, problem=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['problems'].choices = grouped_problems(None, problem.contest, multiple=True)
        self.fields['problems'].initial = (problem,)


"""=================================================== Assignment ==================================================="""


class AssignmentForm(forms.ModelForm):
    user = UserChoiceField(queryset=User.objects.none(), label="Студент")

    class Meta:
        model = Assignment
        fields = ['user', 'problem', 'score', 'score_max', 'score_is_locked', 'submission_limit', 'remark']

    def __init__(self, course, *args, contest=None, user=None, debts=False, **kwargs):
        super().__init__(*args, **kwargs)
        if debts:
            user_ids = Account.students.enrolled().debtors(course).values_list('user_id')
            self.fields['user'].queryset = User.objects.filter(id__in=user_ids)
        else:
            user_ids = Account.students.enrolled().current(course).values_list('user_id')
            self.fields['user'].queryset = User.objects.filter(id__in=user_ids)
        if user:
            self.fields['user'].initial = user
        self.fields['problem'].choices = grouped_problems(course, contest)
        self.fields['score'].widget.attrs['max'] = 5
        self.fields['score_max'].widget.attrs['max'] = 5


class AssignmentUpdateForm(AssignmentForm):
    user = UserChoiceField(queryset=User.objects.all(), label="Студент", disabled=True)

    class Meta(AssignmentForm.Meta):
        pass

    def __init__(self, course, *args, contest=None, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)
        self.fields['problem'].choices = grouped_problems(course, contest)
        self.fields['score'].widget.attrs['max'] = 5
        self.fields['score_max'].widget.attrs['max'] = 5


class AssignmentSetForm(forms.Form):
    contest = forms.ModelChoiceField(queryset=Contest.objects.none(), label="Раздел")
    limit_per_user = forms.IntegerField(min_value=1, max_value=5, initial=1, label="Дополнить до")

    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contest'].queryset = course.contest_set.all()
        self.fields['limit_per_user'].append_text = "заданий"


# TODO: refactor
def grouped_problems(course, contest, multiple=False):
    grouped = []
    if not multiple:
        grouped.append((0, '---------'))
    if contest:
        contests = [contest]
    else:
        contests = course.contest_set.all()
    for contest in contests:
        problems = []
        for problem in contest.problem_set.all():
            problems.append((problem.id, problem))
        group = (contest, problems)
        grouped.append(group)
    return grouped


"""=================================================== Submission ==================================================="""


class SubmissionForm(AttachmentForm):
    FILES_MIN = 1

    class Meta:
        model = Submission
        fields = []

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        self.problem = kwargs.pop('problem', None)
        super().__init__(*args, **kwargs)

    def clean_files(self):
        files = super().clean_files()
        submission_patterns = self.problem.submission_patterns.all()
        if submission_patterns.exists():
            patterns = []
            for submission_pattern in submission_patterns:
                patterns.extend(submission_pattern.pattern.split())
            if len(patterns) != len(files):
                raise ValidationError('Количество файлов не соответствует комплекту поставки решения',
                                      code='no_match')
            label = None
            for f in files:
                for ptn in patterns:
                    match = re.match(ptn, f.name)
                    if match:
                        patterns.remove(ptn)
                        if label is None:
                            label = match.group(1)
                        elif label != match.group(1):
                            raise ValidationError('Идентификаторы в именах файлов не совпадают',
                                                  code='label_mismatch')
                        break
                else:
                    raise ValidationError('Некорректное имя файла: %(filename)s',
                                          code='invalid_filename',
                                          params={'filename': f.name})
            if int(label[-2:]) != self.problem.number:
                raise ValidationError('Идентификатор %(label)s не соответствует комплекту поставки решения',
                                      code='wrong_label',
                                      params={'label': label})
        return files

    def clean(self):
        if self.problem.is_testable:
            last_submission = self.problem.get_latest_submission_by(self.owner)
            if last_submission and last_submission.is_un:
                raise ValidationError('Последнее присланное решение еще не проверено',
                                      code='last_submission_is_un')
        try:
            assignment = Assignment.objects.get(user=self.owner, problem=self.problem)
        except ObjectDoesNotExist:
            pass
        else:
            nsubmissions = Submission.objects.filter(owner=self.owner, problem=self.problem).count()
            if nsubmissions >= assignment.submission_limit:
                raise ValidationError('Количество попыток исчерпано',
                                      code='limit_reached')
        return super().clean()


class SubmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['status']

    def clean_status(self):
        if self.instance.problem.is_testable:
            raise ValidationError('Посылки к этой задаче проверяются автоматически',
                                  code='problem_is_testable')
        return self.cleaned_data['status']


class ToSubmissionsChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{}: {}, {}".format(obj.owner.account, obj.status, naturaltime(obj.date_created))


class SubmissionMossForm(forms.Form):
    to_submissions = ToSubmissionsChoiceField(queryset=Submission.objects.none(), required=True,
                                              label="С посылками")

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission')
        super().__init__(*args, **kwargs)
        to_submissions = (Submission.objects.filter(problem_id=self.submission.problem_id,
                                                    owner__account__enrolled=True)
                                            .exclude(owner_id=self.submission.owner_id))
        self.fields['to_submissions'].queryset = to_submissions


"""===================================================== Event ======================================================"""


class EventForm(forms.ModelForm):
    tutor = UserChoiceField(queryset=User.objects.filter(groups__name='Преподаватель'), required=False,
                            label="Преподаватель")

    class Meta:
        model = Event
        fields = ['tutor', 'title', 'type', 'place', 'date_start', 'date_end', 'tags']


"""====================================================== Test ======================================================"""


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'satisfactorily_percentage', 'good_percentage', 'excellent_percentage']

    def save(self, commit=True):
        super().save(commit)
        try:
            self.instance.problem.title = self.instance.title
            self.instance.problem.description = self.instance.description
            self.instance.problem.number = self.instance.number
            self.instance.problem.save()
        except Problem.DoesNotExist:
            self.instance.problem = Problem.objects.create(owner=self.owner,
                                                           contest=self.contest,
                                                           title=self.title,
                                                           description=self.description,
                                                           number=Problem.objects.get_new_number(self.contest),
                                                           is_testable=False)
        return self.instance


class QuestionMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class QuestionSetForm(forms.Form):
    questions = QuestionMultipleChoiceField(queryset=Question.objects.none(), required=True, label="Выберите задачи")

    def __init__(self, test, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = test.contest.question_set.exclude(id__in=test.questions.values_list('id', flat=True))
        self.fields['questions'].queryset = questions
        self.fields['questions'].widget = SelectMultiple(choices=self.fields['questions'].choices)


"""=================================================== Question ===================================================="""


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'description', 'type', 'number', 'score_max']

    def __init__(self, *args, **kwargs):
        contest = kwargs.pop('contest', None)
        super().__init__(*args, **kwargs)
        if contest:
            self.instance.contest = contest

    def clean_number(self):
        number = self.cleaned_data['number']

        contest = self.instance.contest
        if number in contest.question_set.exclude(id=self.instance.id).values_list('number', flat=True):
            raise ValidationError("Этот номер уже занят.")

        return number


class QuestionExtendedForm(forms.ModelForm):
    number_in_test = forms.IntegerField(min_value=1, required=True, label="Номер в наборе")

    class Meta:
        model = Question
        fields = ['title', 'description', 'type', 'number', 'score_max']

    def __init__(self, *args, **kwargs):
        contest = kwargs.pop('contest', None)
        test = kwargs.pop('test', None)

        super().__init__(*args, **kwargs)
        if contest:
            self.instance.contest = contest
        if test:
            self.storage = {'test': test}

    def clean_number_in_test(self):
        number_in_test = self.cleaned_data['number_in_test']

        test = self.storage['test']
        if number_in_test in test.testmembership_set.values_list('number', flat=True):
            raise ValidationError("Этот номер уже занят.")

        return number_in_test

    def clean_number(self):
        number = self.cleaned_data['number']

        contest = self.instance.contest
        if number in contest.question_set.exclude(id=self.instance.id).values_list('number', flat=True):
            raise ValidationError("Этот номер уже занят.")

        return number

    def save(self, commit=True):
        instance = super().save(commit)
        TestMembership.objects.create(test=self.storage['test'],
                                      question=instance,
                                      number=self.cleaned_data['number_in_test'])
        return instance


"""==================================================== Option ====================================================="""


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_right']


"""==================================================== Answer ====================================================="""


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'file', 'options']

    def __init__(self, *args, question, **kwargs):
        super().__init__(*args, **kwargs)

        if question.type == 1:
            self.fields['text'].required = True
        elif question.type == 3:
            self.fields['file'].required = True
        elif question.type == 2:
            if question.option_set.count():
                if question.option_set.filter(is_right=True).count() > 1:
                    self.fields['options'] = forms.ModelMultipleChoiceField(required=True,
                                                                            label="Варианты",
                                                                            queryset=question.option_set.all(),
                                                                            widget=forms.CheckboxSelectMultiple())
                else:
                    widget = forms.RadioSelect()
                    widget.allow_multiple_selected = True
                    self.fields['options'] = forms.ModelMultipleChoiceField(required=True,
                                                                            label="Варианты",
                                                                            queryset=question.option_set.all(),
                                                                            widget=widget)
            else:
                self.fields['options'] = forms.ModelMultipleChoiceField(required=False,
                                                                        label="Варианты",
                                                                        queryset=question.option_set.none(),
                                                                        widget=forms.HiddenInput())


class AnswerCheckForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Answer.STATUS_CHOICES, required=True, label="Статус")

    class Meta:
        model = Answer
        fields = ['status', 'score']


"""================================================ TestMembership ================================================="""


class TestMembershipForm(forms.ModelForm):
    class Meta:
        model = TestMembership
        fields = ['number']
