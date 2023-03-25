import datetime
import os
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.template.defaultfilters import date, filesizeformat
from django.utils import timezone

from accounts.models import Account
from contest.widgets import OptionCheckboxSelect, OptionRadioSelect
from contests.models import (Assignment, Attachment, Attendance, Contest, Course, CourseLeader, Credit, FNTest, Option,
                             Problem, Submission, SubmissionPattern, SubProblem, UTTest)


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} {}".format(obj.last_name, obj.first_name)


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{} {}".format(obj.last_name, obj.first_name)


class AccountSelect(forms.Select):
    def __init__(self, attrs=None, choices=(), option_attrs=None):
        super().__init__(attrs, choices)
        self.option_attrs = option_attrs

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if self.option_attrs is not None:
            for data_attr, values in self.option_attrs.items():
                option['attrs'][data_attr] = values[getattr(option['value'], 'value', option['value'])]
        return option


class AccountSelectMultiple(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=(), option_attrs=None):
        super().__init__(attrs, choices)
        self.option_attrs = option_attrs

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if self.option_attrs is not None:
            for data_attr, values in self.option_attrs.items():
                option['attrs'][data_attr] = values[getattr(option['value'], 'value', option['value'])]
        return option


class MediaAttachmentMixin:
    FILE_SIZE_LIMIT = 256 * 1024 * 1024
    FILES_SIZE_LIMIT = 640 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                                '.pdf', '.csv', '.aac', '.flac', '.mp3', '.wav', '.wma', '.webm', '.mkv', '.avi',
                                '.mov', '.wmv', '.mp4', '.zip', '.djvu', '.sav']


class SubmissionFilesAttachmentMixin:
    FILE_SIZE_LIMIT = 20 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.png', '.jpg',
                                '.jpeg']


"""=================================================== Attachment ==================================================="""


class AttachmentForm(forms.ModelForm):
    FILE_SIZE_LIMIT = 1024 * 1024
    FILES_MAX = 10
    FILES_MIN = 0
    FILES_SIZE_LIMIT = -1
    FILES_ALLOWED_NAMES = tuple()
    FILES_ALLOWED_EXTENSIONS = ['.c', '.cpp', '.h', '.hpp', '.txt', '.xls', '.xlsx']

    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False, label="Файлы")

    class Meta:
        abstract = True
        model = Attachment
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files'].help_text = ("Можно загрузить до {} файлов. Размер каждого файла не должен превышать {}"
                                          .format(self.FILES_MAX, filesizeformat(self.FILE_SIZE_LIMIT)))

    def get_files_size_limit(self):
        if self.FILES_SIZE_LIMIT == -1:
            return self.FILES_MAX * self.FILE_SIZE_LIMIT
        else:
            return self.FILES_SIZE_LIMIT

    def clean_files(self):
        if not self.files and self.FILES_MIN == 0:
            return self.files
        elif not self.files:
            raise ValidationError(
                'Выберите хотя бы %(files_min)i файл для загрузки',
                code='not_enough_files',
                params={'files_min': self.FILES_MIN}
            )
        files = self.files.getlist('files')
        if len(files) > self.FILES_MAX:
            raise ValidationError(
                'Слишком много файлов. Допустимо загружать не более %(files_max)i',
                code='too_many_files',
                params={'files_max': self.FILES_MAX}
            )
        else:
            files_size = 0
            for file in files:
                if file.size > self.FILE_SIZE_LIMIT:
                    raise ValidationError(
                        'Размер каждого файла не должен превышать %(file_size_limit)s',
                        code='large_file',
                        params={'file_size_limit': filesizeformat(self.FILE_SIZE_LIMIT)}
                    )
                filename = os.path.splitext(file.name)
                if not filename[1].lower() in self.FILES_ALLOWED_EXTENSIONS:
                    if not filename[0].startswith(self.FILES_ALLOWED_NAMES):
                        raise ValidationError(
                            'Допустимы только файлы с расширениями: %(files_allowed_extensions)s',
                            code='invalid_extension',
                            params={'files_allowed_extensions': ', '.join(self.FILES_ALLOWED_EXTENSIONS)}
                        )
                files_size += file.size
            files_size_limit = self.get_files_size_limit()
            if files_size > files_size_limit:
                raise ValidationError(
                    'Размер всех файлов не должен превышать %(files_size_limit)s',
                    code='large_files',
                    params={'files_size_limit': filesizeformat(files_size_limit)}
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
    class Meta:
        model = Course
        fields = ['faculty', 'title_official', 'title_unofficial', 'description', 'level', 'soft_deleted']


class CourseFinishForm(forms.Form):
    level_ups = UserMultipleChoiceField(queryset=Account.objects.none(), required=True, label="Выберите студентов")

    def __init__(self, level_ups_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level_ups'].queryset = level_ups_queryset
        self.fields['level_ups'].initial = level_ups_queryset.filter(credit_score__gte=3)


"""================================================== CourseLeader =================================================="""


class CourseLeaderForm(forms.ModelForm):
    leader = UserChoiceField(queryset=User.objects.none(), label="Преподаватель")

    class Meta:
        model = CourseLeader
        fields = ['course', 'leader', 'group', 'subgroup']
        widgets = {'course': forms.HiddenInput}

    def __init__(self, *args, course, leader_queryset, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].initial = course
        self.fields['leader'].queryset = leader_queryset
        option_subtext_data = leader_queryset.values_list('pk', 'account__faculty__short_name')
        option_subtext_data = {pk: faculty_short_name for pk, faculty_short_name in option_subtext_data}
        option_subtext_data[''] = ''
        option_attrs = {'data-subtext': option_subtext_data}
        self.fields['leader'].widget = AccountSelect(choices=self.fields['leader'].choices, option_attrs=option_attrs)


"""===================================================== Credit ====================================================="""


class CreditUpdateForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['score']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].help_text = "последнее изменение: " + date(self.instance.date_updated, 'd M Y г. в H:i')


class CreditSetForm(forms.Form):
    runner_ups = UserMultipleChoiceField(queryset=Account.objects.none(), required=True, label="Выберите студентов")

    def __init__(self, course, runner_ups_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['runner_ups'].queryset = runner_ups_queryset
        self.fields['runner_ups'].initial = runner_ups_queryset.filter(level__in=[course.level - 1, course.level])


class CreditReportForm(forms.Form):
    TYPE_CHOICES = (
        ("Экзамен", "Экзамен"),
        ("Зачёт", "Зачёт"),
    )

    group = forms.ChoiceField(choices=Account.GROUP_CHOICES, required=False, label="Выберите группу")
    group_name = forms.CharField(required=False, label="Название группы")
    students = UserMultipleChoiceField(queryset=Account.objects.none(), required=False, label="Выберите студентов")
    type = forms.ChoiceField(choices=TYPE_CHOICES, label="Тип ведомости")
    examiners = UserMultipleChoiceField(queryset=Account.objects.none(), label="Выберите экзаменаторов")
    faculty = forms.CharField(label="Факультет")
    discipline = forms.CharField(label="Дисциплина")
    semester = forms.IntegerField(label="Семестр")
    date = forms.DateField(label="Дата")

    def __init__(self, course, students, examiners, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['students'].queryset = students
        option_subtext_data = students.values_list('pk', 'level', 'faculty__short_name')
        level_displays = dict(Account.LEVEL_CHOICES)
        option_subtext_data = {pk: "{}, {}".format(faculty, level_displays[level]) for pk, level, faculty in
                               option_subtext_data}
        option_subtext_data[''] = ''
        option_attrs = {'data-subtext': option_subtext_data}
        self.fields['students'].widget = AccountSelectMultiple(choices=self.fields['students'].choices,
                                                               option_attrs=option_attrs)
        self.fields['examiners'].queryset = examiners
        self.fields['examiners'].initial = course.leaders.all()
        self.fields['faculty'].initial = course.faculty.short_name
        self.fields['discipline'].initial = course.title_official
        self.fields['semester'].initial = course.level
        self.fields['date'].initial = timezone.localdate()
        self.storage = {'students': students, 'course': course}

    def clean(self):
        group = self.cleaned_data.get('group')
        if group is not None and group.isdigit() and int(group) > 0:
            self.cleaned_data['group_name'] = Account.make_group_name(self.storage['course'].faculty.group_prefix,
                                                                      group, self.storage['course'].level)
            self.cleaned_data['students'] = self.storage['students'].filter(group=group)
            if not self.cleaned_data['students'].exists():
                self.add_error('group', ValidationError("В выбранной группе нет студентов", code='group_is_empty'))
        else:
            if self.cleaned_data['group_name'] == '':
                self.add_error('group_name',
                               ValidationError("Название группы требуется, если не выбрана группа из списка",
                                               code='group_name_required'))
            if len(self.cleaned_data['students']) == 0:
                self.add_error('students',
                               ValidationError("Следует выбрать хотя бы одного студента, если не выбрана группа из "
                                               "списка", code='students_required'))
            self.add_error('group', ValidationError("Выберите группу или введите название группы и выберите студентов",
                                                    code='group_required'))
        return self.cleaned_data


"""=================================================== Attendance ==================================================="""


def get_time_interval_choices_and_initial():
    now = timezone.localtime()
    today = now.date()
    choices = [(datetime.time(9), "1 пара (09:00 - 10:30)"),
               (datetime.time(10, 45), "2 пара (10:45 - 12:15)"),
               (datetime.time(13, 15), "3 пара (13:15 - 14:45)"),
               (datetime.time(15), "4 пара (15:00 - 16:30)"),
               (datetime.time(16, 45), "5 пара (16:45 - 18:15)"),
               (datetime.time(18, 30), "6 пара (18:30 - 20:00)")]
    initial = choices[0]
    for choice, _ in choices:
        combined = datetime.datetime.combine(today, choice)
        if now > timezone.make_aware(combined):
            initial = choice
    return choices, initial


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user', 'course', 'flag', 'date_from', 'date_to']
        widgets = {'user': forms.HiddenInput, 'course': forms.HiddenInput, 'date_from': forms.HiddenInput,
                   'date_to': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = kwargs.get('initial').get('user').account


class AttendanceDateForm(forms.Form):
    date = forms.DateField(label="Дата")
    time_interval = forms.ChoiceField(label="Время")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.localdate()
        choices, initial = get_time_interval_choices_and_initial()
        self.fields['time_interval'].choices = choices
        self.fields['time_interval'].initial = initial

    def clean_date(self):
        date = self.cleaned_data['date']
        if timezone.localdate() < date:
            raise ValidationError("Выбранная дата еще не наступила.", code='date_in_future')
        return self.cleaned_data['date']

    def clean(self):
        if all(k in self.cleaned_data for k in ('date', 'time_interval')):
            datetime_combined = self.get_date()
            if timezone.localtime() < timezone.make_aware(datetime_combined):
                self.add_error('time_interval', ValidationError("Выбранная пара еще не началась.",
                                                                code='datetime_in_future'))
        return self.cleaned_data

    def get_date(self):
        time = datetime.datetime.strptime(self.cleaned_data['time_interval'], '%H:%M:%S').time()
        return datetime.datetime.combine(self.cleaned_data['date'], time)


class AttendanceFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, date=None, **kwargs):
        super().__init__(*args, **kwargs)
        if date is not None:
            date_from, date_to = date, date + datetime.timedelta(minutes=90)
            for i in range(self.total_form_count()):
                self.data.update(dict([(self.add_prefix(i) + '-date_from', date_from),
                                       (self.add_prefix(i) + '-date_to', date_to)]))

    def clean(self):
        if self.total_form_count() == 0:
            raise ValidationError("В таблице нет ни одного студента.", code='empty_formset')
        if any(filter(lambda x: '__all__' in x, self.errors)):
            raise ValidationError("Посещаемость студентов в выбранном интервале уже отмечена.")
        return super().clean()


"""==================================================== Contest ====================================================="""


class ContestAttachmentForm(MediaAttachmentMixin, AttachmentForm):
    class Meta:
        model = Contest
        fields = []


class ContestForm(ContestAttachmentForm):
    class Meta:
        model = Contest
        fields = ['course', 'title', 'description', 'number', 'hidden', 'soft_deleted']
        widgets = {'course': forms.HiddenInput}
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Раздел с таким номером уже существует в этом курсе.",
            }
        }


class ContestMoveForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['course', 'number', 'soft_deleted']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Раздел с таким номером уже существует в этом курсе.",
            }
        }

    def __init__(self, course_queryset=None, **kwargs):
        super().__init__(**kwargs)
        self.fields['course'].queryset = course_queryset


"""==================================================== Problem ====================================================="""


class ProblemAttachmentForm(MediaAttachmentMixin, AttachmentForm):
    class Meta:
        model = Problem
        fields = []


class ProblemForm(ProblemAttachmentForm):
    class Meta(ProblemAttachmentForm.Meta):
        fields = ['contest', 'type', 'title', 'description', 'number', 'soft_deleted', 'score_max', 'score_for_5',
                  'score_for_4', 'score_for_3', 'difficulty']
        widgets = {'contest': forms.HiddenInput, 'type': forms.HiddenInput}
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Задача с таким номером уже существует в этом разделе.",
            }
        }

    def clean(self):
        if not (self.cleaned_data['score_for_3'] <= self.cleaned_data['score_for_4'] <= self.cleaned_data['score_for_5']):
            raise ValidationError("Критерии должны быть упорядочены", code='criteria_invalid_order')
        if self.cleaned_data['score_for_3'] < 1:
            raise ValidationError("Критерии не могут быть меньше 1", code='criteria_less_than_1')
        if self.cleaned_data['score_for_5'] > self.cleaned_data['score_max']:
            raise ValidationError("Критерии не могут быть больше максимального балла",
                                  code='criteria_exceeds_score_max')
        return super().clean()


class ProblemMoveForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['contest', 'number', 'soft_deleted']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Задача с таким номером уже существует в этом разделе.",
            }
        }

    def __init__(self, contest_queryset=None, **kwargs):
        super().__init__(**kwargs)
        self.fields['contest'].queryset = contest_queryset
        self.fields['contest'].choices = grouped_contests(contest_queryset)


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
        widgets = {'contest': forms.HiddenInput, 'type': forms.HiddenInput, 'score_max': forms.HiddenInput}
        labels = {'score_for_5': "Процентов для 5", 'score_for_4': "Процентов для 4", 'score_for_3': "Процентов для 3"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sub_problems'].queryset = Problem.objects.filter(contest=self.initial['contest'],
                                                                      type__in=['Program', 'Files', 'Text', 'Options'])

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
    submissions = forms.ModelMultipleChoiceField(queryset=Submission.objects.none(), required=False, label="Посылки")

    def __init__(self, *args, problem_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submissions'].queryset = Submission.objects.to_rollback(problem_id)


# TODO: refactor
def grouped_contests(contests, multiple=False):
    grouped = []
    if not multiple:
        grouped.append((0, '---------'))
    course_contests = {}
    for contest in contests:
        if contest.course not in course_contests:
            course_contests[contest.course] = [(contest.id, contest)]
        else:
            course_contests[contest.course].append((contest.id, contest))
    for course, contest_choices in course_contests.items():
        group = (course, contest_choices)
        grouped.append(group)
    return grouped


"""=================================================== SubProblem ==================================================="""


class SubProblemForm(forms.ModelForm):
    class Meta:
        model = SubProblem
        fields = ['problem', 'number']
        widgets = {'problem': forms.HiddenInput}
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "Такой номер подзадачи уже занят в тесте",
            }
        }


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


class AssignmentUpdateAttachmentForm(SubmissionFilesAttachmentMixin, AttachmentForm):
    class Meta:
        model = Assignment
        fields = []


class AssignmentEvaluateForm(AssignmentUpdateAttachmentForm):
    class Meta:
        model = Assignment
        fields = ['score', 'score_max', 'score_is_locked', 'submission_limit', 'remark', 'deadline']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['score'].widget.attrs['max'] = 5
        self.fields['score_max'].widget.attrs['max'] = 5

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline is not None and 'deadline' in self.changed_data and deadline <= timezone.now():
            raise ValidationError("Укажите дату в будущем", code='invalid_deadline')
        return deadline

    def clean(self):
        super().clean()
        if self.cleaned_data['score'] > self.cleaned_data['score_max']:
            raise ValidationError("Оценка не может превышать максимальную оценку", code='score_gt_score_max')
        return self.cleaned_data


class AssignmentUpdateForm(AssignmentEvaluateForm):
    user = UserChoiceField(queryset=User.objects.none(), label="Студент", disabled=True)

    class Meta(AssignmentEvaluateForm.Meta):
        fields = AssignmentEvaluateForm.Meta.fields + ['user', 'problem']

    def __init__(self, user_queryset, course, contest=None, **kwargs):
        super().__init__(**kwargs)
        self.fields['user'].queryset = user_queryset
        self.fields['problem'].choices = grouped_problems(course, contest)


class AssignmentForm(AssignmentUpdateForm):
    user = UserChoiceField(queryset=User.objects.none(), label="Студент")

    class Meta(AssignmentUpdateForm.Meta):
        pass

    def __init__(self, user_queryset, course, contest=None, user=None, **kwargs):
        super().__init__(user_queryset, course, contest, **kwargs)
        if user is not None:
            self.fields['user'].initial = user


class AssignmentSetForm(forms.Form):
    contest = forms.ModelChoiceField(queryset=Contest.objects.none(), label="Раздел")
    type = forms.ChoiceField(choices=Problem.TYPE_CHOICES, initial='Program', label="Тип задач")
    limit_per_user = forms.IntegerField(min_value=1, max_value=20, initial=1, label="Дополнить до",
                                        help_text="Количество заданий в выбранном разделе увеличится до указанного "
                                                  "значения у каждого студента")
    submission_limit = forms.IntegerField(initial=Assignment.DEFAULT_SUBMISSION_LIMIT,
                                          label="Ограничить количество посылок до",
                                          help_text="Каждый студент сможет отправить до указанного количества посылок "
                                                    "по каждому новому заданию")
    deadline = forms.DateTimeField(required=False, label="Принимать посылки до")

    def __init__(self, course, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contest'].queryset = course.contest_set.all()
        self.fields['limit_per_user'].append_text = "заданий"

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline is not None and deadline <= timezone.now():
            raise ValidationError("Укажите дату в будущем", code='invalid_deadline')
        return deadline


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


class SubmissionForm(forms.ModelForm):
    class Meta:
        abstract = True
        model = Submission
        fields = []

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        self.problem = kwargs.pop('problem')
        self.assignment = kwargs.pop('assignment')
        self.main_submission = kwargs.pop('main_submission', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.assignment is None and not self.owner.is_superuser:
            raise ValidationError("Посылку можно отправить к задаче только по заданию. "
                                  "Этой задачи нет среди Ваших заданий.", code='no_assignment')
        if self.problem.is_testable:
            last_submission = self.problem.get_latest_submission_by(self.owner)
            if last_submission and last_submission.is_un:
                raise ValidationError("Последнее присланное решение еще не проверено",
                                      code='last_submission_is_un')
        if self.assignment is not None:
            if not self.assignment.credit_incomplete and not self.owner.is_superuser:
                raise ValidationError("Невозможно отправить посылку к задаче завершенного курса",
                                      code='assignment_credit_complete')
            if self.assignment.deadline is not None and self.assignment.deadline < timezone.now():
                raise ValidationError("Время приема посылок по Вашему заданию истекло",
                                      code='assignment_deadline_reached')
            submission_count = self.assignment.submission_set.count()
            if submission_count >= self.assignment.submission_limit and self.main_submission is None:
                raise ValidationError("Количество попыток исчерпано", code='submission_limit_reached')
        return super().clean()


class SubmissionAttachmentForm(SubmissionForm, AttachmentForm):
    FILES_MIN = 1

    class Meta:
        abstract = True
        model = Submission
        fields = []


class SubmissionProgramForm(SubmissionAttachmentForm):
    class Meta:
        model = Submission
        fields = []

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
                for pattern in patterns:
                    match = re.match(pattern, f.name)
                    if match:
                        patterns.remove(pattern)
                        if match.lastindex > 0:
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


class SubmissionTextForm(SubmissionForm):
    class Meta:
        model = Submission
        fields = ['text', 'footprint']
        widgets = {'footprint': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_text(self):
        if self.cleaned_data['text'].strip() == "":
            raise ValidationError("Текст ответа не может быть пустым", code='text_empty')
        return self.cleaned_data['text']


class SubmissionVerbalForm(SubmissionAttachmentForm):
    FILE_SIZE_LIMIT = 20 * 1024 * 1024
    FILES_ALLOWED_EXTENSIONS = ['.aac', '.flac', '.mp3', '.wav', '.wma']

    class Meta:
        model = Submission
        fields = []


class SubmissionFilesForm(SubmissionFilesAttachmentMixin, SubmissionAttachmentForm):
    class Meta:
        model = Submission
        fields = []


class SubmissionOptionsForm(SubmissionForm):
    class Meta:
        model = Submission
        fields = ['options']
        error_messages = {
            'options': {
                'required': "Не выбран ни один вариант ответа."
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = self.problem.option_set.order_randomly()
        self.fields['options'].queryset = options
        if options.filter(is_correct=True).count() > 1:
            widget_class = OptionCheckboxSelect
        else:
            widget_class = OptionRadioSelect
            widget_class.allow_multiple_selected = True
        self.fields['options'].widget = widget_class(choices=self.fields['options'].choices)


class SubmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['status', 'score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.attrs['max'] = self.instance.problem.score_max
        self.fields['score'].required = False
        self.fields['status'].required = False
        if self.instance.problem.type != 'Program':
            self.fields['status'].choices = [
                ('OK', "Задача решена"),
                ('PS', "Задача решена частично"),
                ('TF', "Тест провален"),
                ('WA', "Неверный ответ"),
                ('NA', "Ответ отсутствует"),
                ('EV', "Посылка проверяется"),
                ('UN', "Посылка не проверена")
            ]

    def clean_score(self):
        score = self.cleaned_data['score']
        if score is not None and score > self.instance.problem.score_max:
            raise ValidationError("Оценка не может превышать максимальную оценку этой задачи",
                                  code='score_exceeds_problem_score_max')
        return score

    def clean(self):
        if self.instance.problem.type == 'Program' and self.instance.problem.is_testable:
            raise ValidationError("Посылки к этой задаче проверяются автоматически", code='problem_is_testable')
        return super().clean()

    def save(self, commit=True):
        instance = super().save(commit)
        if 'status' in self.changed_data and 'score' not in self.changed_data:
            status = self.cleaned_data['status']
            if status == 'OK':
                instance.score = instance.problem.score_max
            elif status == 'WA':
                instance.score = 0
            instance = super().save(commit)
        if 'score' in self.changed_data and 'status' not in self.changed_data:
            score = self.cleaned_data['score']
            if score >= instance.problem.score_for_5:
                instance.status = 'OK'
            elif score >= instance.problem.score_for_3:
                instance.status = 'PS'
            else:
                instance.status = 'WA'
            instance = super().save(commit)
        if instance.main_submission is not None:
            if 'status' in self.changed_data:
                instance.main_submission.update_test_status()
                instance.main_submission.update_test_score()
            if 'score' in self.changed_data:
                instance.main_submission.update_test_score()
                instance.main_submission.update_test_status()
        return super().save(commit)


class ToSubmissionsChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{}: {}, {}".format(obj.owner.account, obj.status, naturaltime(obj.date_created))


class SubmissionMossForm(forms.Form):
    to_submissions = ToSubmissionsChoiceField(queryset=Submission.objects.none(), required=True, label="С посылками")

    def __init__(self, to_submissions_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_submissions'].queryset = to_submissions_queryset
