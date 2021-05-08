import os
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.template.defaultfilters import filesizeformat

from accounts.models import Account
from contest.widgets import BootstrapCheckboxSelect, BootstrapRadioSelect
from contests.models import (Assignment, Attachment, Contest, Course, Event, FNTest, Filter, Option, Problem,
                             SubProblem, Submission, SubmissionPattern, UTTest)


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
        instance = super().save(commit)
        if self.files:
            files = self.files.getlist('files')
            instance_type = ContentType.objects.get_for_model(instance)
            new_attachments = []
            for file in files:
                new_attachment = Attachment(owner=instance.owner,
                                            object_type=instance_type,
                                            object_id=instance.id,
                                            file=file)
                new_attachments.append(new_attachment)
            Attachment.objects.bulk_create(new_attachments)
        return instance


"""===================================================== Course ====================================================="""


class CourseForm(forms.ModelForm):
    leaders = UserMultipleChoiceField(queryset=User.objects.none(), required=False, label="Ведущие преподаватели")

    class Meta:
        model = Course
        fields = ['leaders', 'faculty', 'title', 'description', 'level']

    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leaders'].queryset = User.objects.filter(groups__name="Преподаватель", account__faculty=faculty)

    def save(self, commit=True):
        instance = super().save(commit)
        for leader in instance.leaders.all():
            Filter.objects.get_or_create(user=leader, course=instance)
        return instance


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


class ContestPartialForm(AttachmentForm):
    FILES_SIZE_LIMIT = 10 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.doc', '.docx', '.ppt', '.pptx', '.pdf']

    class Meta:
        model = Contest
        fields = []


class ContestForm(ContestPartialForm):
    class Meta:
        model = Contest
        fields = ['course', 'title', 'description', 'number']
        widgets = {'course': forms.HiddenInput}


"""==================================================== Problem ====================================================="""


class ProblemAttachmentForm(AttachmentForm):
    FILES_SIZE_LIMIT = 10 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.doc', '.docx', '.ppt', '.pptx', '.pdf']

    class Meta:
        model = Problem
        fields = []


class ProblemForm(ProblemAttachmentForm):
    class Meta(ProblemAttachmentForm.Meta):
        fields = ['contest', 'type', 'title', 'description', 'number', 'score_max', 'score_for_5', 'score_for_4',
                  'score_for_3', 'difficulty']
        widgets = {'contest': forms.HiddenInput, 'type': forms.HiddenInput}

    def clean(self):
        if not (self.cleaned_data['score_for_3'] <= self.cleaned_data['score_for_4'] <= self.cleaned_data['score_for_5']):
            raise ValidationError("Критерии должны быть упорядочены", code='criteria_invalid_order')
        if self.cleaned_data['score_for_3'] < 1:
            raise ValidationError("Критерии не могут быть меньше 1", code='criteria_less_than_1')
        if self.cleaned_data['score_for_5'] > self.cleaned_data['score_max']:
            raise ValidationError("Критерии не могут быть больше максимального балла",
                                  code='criteria_exceeds_score_max')
        return self.cleaned_data


class ProblemProgramForm(ProblemForm):
    class Meta(ProblemForm.Meta):
        fields = ProblemForm.Meta.fields + ['language', 'compile_args', 'launch_args', 'time_limit', 'memory_limit',
                                            'is_testable']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_limit'].append_text = "секунд"
        self.fields['memory_limit'].append_text = "КБайт"


class ProblemCommonForm(ProblemForm):
    pass


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']


class OptionBaseFormSet(forms.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            is_correct = form.cleaned_data.get('is_correct')
            if is_correct:
                return
        raise ValidationError("Хотя бы один вариант должен быть отмечен как верный.")

    def full_clean(self):
        super().full_clean()
        for error in self._non_form_errors.as_data():
            if error.code == 'too_many_forms':
                error.message = "Вариантов ответа не может быть больше %d." % self.max_num
            elif error.code == 'too_few_forms':
                error.message = "Вариантов ответа должно быть как минимум %d." % self.min_num


class ProblemTestForm(ProblemForm):
    class Meta(ProblemForm.Meta):
        fields = ProblemForm.Meta.fields + ['sub_problems']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_problems'].queryset = Problem.objects.filter(contest=self.initial['contest'],
                                                                      type__in=['Program', 'Files', 'Text', 'Options'])
        self.fields['score_for_5'].label = "Процентов для 5"
        self.fields['score_for_4'].label = "Процентов для 4"
        self.fields['score_for_3'].label = "Процентов для 3"
        self.fields['score_max'].widget = forms.HiddenInput()

    def clean_sub_problems(self):
        if len(self.cleaned_data['sub_problems']) <= 1:
            raise ValidationError("Необходимо выбрать как минимум 2 задачи, чтобы сформировать тест",
                                  code='insufficient_sub_problems')
        return self.cleaned_data['sub_problems']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.save()
        first_new_number = SubProblem.objects.get_new_number(instance)
        old_subproblem_ids = set(SubProblem.objects.filter(problem=instance).values_list('sub_problem', flat=True))
        new_subproblems = []
        n = 0
        for sub_problem_id in self.cleaned_data['sub_problems'].values_list('id', flat=True):
            if sub_problem_id in old_subproblem_ids:
                old_subproblem_ids.remove(sub_problem_id)
            else:
                new_subproblems.append(SubProblem(problem=instance, sub_problem_id=sub_problem_id,
                                                  number=first_new_number + n))
                n += 1
        instance.sub_problems.remove(*old_subproblem_ids)
        SubProblem.objects.bulk_create(new_subproblems)
        return instance


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


class AssignmentUpdatePartialForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['score', 'score_max', 'score_is_locked', 'submission_limit', 'remark']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['score'].widget.attrs['max'] = 5
        self.fields['score_max'].widget.attrs['max'] = 5

    def clean(self):
        super().clean()
        if self.cleaned_data['score'] > self.cleaned_data['score_max']:
            raise ValidationError("Оценка не может превышать максимальную оценку", code='score_gt_score_max')
        return self.cleaned_data


class AssignmentUpdateForm(AssignmentUpdatePartialForm):
    user = UserChoiceField(queryset=User.objects.none(), label="Студент", disabled=True)

    class Meta(AssignmentUpdatePartialForm.Meta):
        fields = AssignmentUpdatePartialForm.Meta.fields + ['user', 'problem']

    def __init__(self, course, contest=None, **kwargs):
        super().__init__(**kwargs)
        user_ids = Account.students.enrolled().current(course).values_list('user_id')
        self.fields['user'].queryset = User.objects.filter(id__in=user_ids)
        self.fields['problem'].choices = grouped_problems(course, contest)


class AssignmentForm(AssignmentUpdateForm):
    user = UserChoiceField(queryset=User.objects.none(), label="Студент")

    class Meta(AssignmentUpdateForm.Meta):
        pass

    def __init__(self, course, contest=None, user=None, debts=False, **kwargs):
        super().__init__(course, contest, **kwargs)
        if debts:
            user_ids = Account.students.enrolled().debtors(course).values_list('user_id')
            self.fields['user'].queryset = User.objects.filter(id__in=user_ids)
        if user:
            self.fields['user'].initial = user


class AssignmentSetForm(forms.Form):
    contest = forms.ModelChoiceField(queryset=Contest.objects.none(), label="Раздел")
    type = forms.ChoiceField(choices=Problem.TYPE_CHOICES, initial='Program', label="Тип задач")
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


class SubmissionAttachmentForm(AttachmentForm):
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
                raise ValidationError("Количество файлов не соответствует комплекту поставки решения", code='no_match')
            label = None
            for f in files:
                for ptn in patterns:
                    match = re.match(ptn, f.name)
                    if match:
                        patterns.remove(ptn)
                        if label is None:
                            label = match.group(1)
                        elif label != match.group(1):
                            raise ValidationError("Идентификаторы в именах файлов не совпадают",
                                                  code='label_mismatch')
                        break
                else:
                    raise ValidationError("Некорректное имя файла: %(filename)s", code='invalid_filename',
                                          params={'filename': f.name})
            if int(label[-2:]) != self.problem.number:
                raise ValidationError("Идентификатор %(label)s не соответствует комплекту поставки решения",
                                      code='wrong_label', params={'label': label})
        return files

    def clean(self):
        if self.problem.is_testable:
            last_submission = self.problem.get_latest_submission_by(self.owner)
            if last_submission and last_submission.is_un:
                raise ValidationError("Последнее присланное решение еще не проверено",
                                      code='last_submission_is_un')
        try:
            assignment = Assignment.objects.get(user=self.owner, problem=self.problem)
        except ObjectDoesNotExist:
            pass
        else:
            nsubmissions = Submission.objects.filter(owner=self.owner, problem=self.problem).count()
            if nsubmissions >= assignment.submission_limit:
                raise ValidationError("Количество попыток исчерпано", code='limit_reached')
        return super().clean()


class SubmissionTextForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['text']

    def __init__(self, *args, **kwargs):
        kwargs.pop('owner', None)
        kwargs.pop('problem', None)
        super().__init__(*args, **kwargs)
        self.fields['text'].required = True


class SubmissionFilesForm(AttachmentForm):
    FILES_MIN = 1
    FILES_SIZE_LIMIT = 10 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.txt', '.doc', '.docx', '.ppt', '.pptx', '.pdf', '.png', '.jpg', '.jpeg']

    class Meta:
        model = Submission
        fields = []

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        self.problem = kwargs.pop('problem', None)
        super().__init__(*args, **kwargs)


class SubmissionOptionsForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['options']

    def __init__(self, *args, **kwargs):
        kwargs.pop('owner', None)
        problem = kwargs.pop('problem')
        super().__init__(*args, **kwargs)
        options = problem.option_set.all()
        if options.filter(is_correct=True).count() > 1:
            widget = BootstrapCheckboxSelect()
        else:
            widget = BootstrapRadioSelect()
            widget.allow_multiple_selected = True
        self.fields['options'] = forms.ModelMultipleChoiceField(required=True, label="Варианты",  queryset=options,
                                                                widget=widget)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        instance.update_options_score()
        return instance


class SubmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['status', 'score']

    def clean_score(self):
        if self.cleaned_data['score'] > self.instance.problem.score_max:
            raise ValidationError("Оценка не может превышать максимальную оценку этой задачи",
                                  code='score_exceeds_problem_score_max')
        return self.cleaned_data['score']

    def clean(self):
        if self.instance.problem.is_testable:
            raise ValidationError("Посылки к этой задаче проверяются автоматически", code='problem_is_testable')
        return super().clean()


class ToSubmissionsChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{}: {}, {}".format(obj.owner.account, obj.status, naturaltime(obj.date_created))


class SubmissionMossForm(forms.Form):
    to_submissions = ToSubmissionsChoiceField(queryset=Submission.objects.none(), required=True, label="С посылками")

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
