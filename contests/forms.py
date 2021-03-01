import os
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms.models import BaseInlineFormSet, BaseModelFormSet
from django.template.defaultfilters import filesizeformat

from accounts.models import Account
from contests.models import (Answer, Attachment, Course, Contest, Option, Problem, Solution, TestSubmission, UTTest, FNTest, Assignment, Submission, Event, Test, Question)


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} {}".format(obj.last_name, obj.first_name)


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{} {}".format(obj.last_name, obj.first_name)


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
    runner_ups = forms.ModelMultipleChoiceField(queryset=Account.objects.none(), required=False,
                                                label="Перевести на этот курс и назначить зачет")
    non_credited = forms.ModelMultipleChoiceField(queryset=Account.objects.none(), required=False,
                                                  label="Назначить зачет")

    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        runner_ups = Account.students.enrolled().filter(level=course.level - 1).with_credits()
        self.fields['runner_ups'].queryset = runner_ups
        self.fields['runner_ups'].initial = runner_ups.filter(credit_score__gt=2)
        non_credited = Account.students.enrolled().filter(level=course.level).none_credits()
        self.fields['non_credited'].queryset = non_credited
        self.fields['non_credited'].initial = non_credited


"""==================================================== Contest ====================================================="""


class ContestForm(AttachmentForm):
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.doc', '.docx']

    class Meta:
        model = Contest
        fields = ['title', 'description', 'number']

    def __init__(self, *args, initial_number=Contest.DEFAULT_NUMBER, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].initial = initial_number


"""==================================================== Problem ====================================================="""


class ProblemForm(AttachmentForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'number', 'difficulty', 'language', 'compile_args', 'launch_args',
                  'time_limit', 'memory_limit', 'is_testable']

    def __init__(self, *args, initial_number=Problem.DEFAULT_NUMBER, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].initial = initial_number
        self.fields['time_limit'].append_text = "секунд"
        self.fields['memory_limit'].append_text = "КБайт"


class ProblemRollbackResultsForm(forms.Form):
    submissions = forms.ModelMultipleChoiceField(Submission.objects.none(), label="Посылки")

    def __init__(self, *args, problem_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submissions'].queryset = Submission.objects.to_rollback(problem_id)


"""==================================================== Solution ===================================================="""


class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
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
            self.fields['user'].queryset = User.objects.filter(id__in=Account.students.enrolled()
                                                               .debtors(course.level).values_list('user_id'))
        else:
            self.fields['user'].queryset = User.objects.filter(id__in=Account.students.enrolled()
                                                               .filter(level=course.level).values_list('user_id'))
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
        solutions = self.problem.solution_set.all()
        if solutions.exists():
            patterns = []
            for solution in solutions:
                patterns.extend(solution.pattern.split())
            if len(patterns) != len(files):
                raise ValidationError(
                    'Количество файлов не соответствует комплекту поставки решения',
                    code='no_match'
                )
            label = None
            for f in files:
                for ptn in patterns:
                    match = re.match(ptn, f.name)
                    if match:
                        patterns.remove(ptn)
                        if label is None:
                            label = match.group(1)
                        elif label != match.group(1):
                            raise ValidationError(
                                'Идентификаторы в именах файлов не совпадают',
                                code='label_mismatch'
                            )
                        break
                else:
                    raise ValidationError(
                        'Некорректное имя файла: %(filename)s',
                        code='invalid_filename',
                        params={'filename': f.name}
                    )
            if int(label[-2:]) != self.problem.number:
                raise ValidationError(
                    'Идентификатор %(label)s не соответствует комплекту поставки решения',
                    code='wrong_label',
                    params={'label': label}
                )
        return files

    def clean(self):
        last_submission = self.problem.get_latest_submission_by(self.owner)
        if last_submission and last_submission.is_un:
            raise ValidationError(
                'Последнее присланное решение еще не проверено',
                code='last_submission_is_un'
            )
        try:
            assignment = Assignment.objects.get(user=self.owner, problem=self.problem)
        except ObjectDoesNotExist:
            pass
        else:
            nsubmissions = Submission.objects.filter(owner=self.owner, problem=self.problem).count()
            if nsubmissions >= assignment.submission_limit:
                raise ValidationError(
                    'Количество попыток исчерпано',
                    code='limit_reached'
                )
        return super().clean()


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
        fields = ['title', 'description']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'answer_type', 'number']

    def clean_number(self):
        number = self.cleaned_data['number']
        test = self.instance.test

        if number != self.instance.number and number in test.question_set.values_list('number', flat=True):
            raise ValidationError("Этот номер уже занят.")

        return number


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_right']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'file', 'options']

    def __init__(self, *args, question, **kwargs):
        super().__init__(*args, **kwargs)

        if question.answer_type == 1:
            self.fields['text'].required = True
        elif question.answer_type == 2:
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
        elif question.answer_type == 3:
            self.fields['file'].required = True
