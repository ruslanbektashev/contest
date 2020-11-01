import importlib
import io
import os
import random
import zipfile

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_comma_separated_integer_list, MinValueValidator, MaxValueValidator
from django.db import models
from django.dispatch import receiver
from django.urls import reverse

from contest.abstract import CDEntry, CRDEntry, CRUDEntry
from accounts.models import Account, Comment, Activity, Subscription

try:
    from tools.sandbox import Sandbox
    from tools.utility import Status, diff
except ImportError:
    from contest.utils import Sandbox, Status, diff

"""=================================================== Attachment ==================================================="""


def attachment_path(instance, filename):
    return "attachments/{app_label}/{model}/{id}/{filename}".format(
        app_label=instance.object._meta.app_label.lower(),
        model=instance.object._meta.object_name.lower(),
        id=instance.object.id,
        filename=filename
    )


class Attachment(CDEntry):
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey(ct_field='object_type')

    file = models.FileField(upload_to=attachment_path, verbose_name="Файл")

    class Meta(CDEntry.Meta):
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    @property
    def dirname(self):
        return os.path.split(self.file.path)[0]

    @property
    def filename(self):
        return os.path.split(self.file.name)[1]

    def __str__(self):
        return "%s" % self.filename


@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """ deletes file from filesystem when corresponding `Attachment` object is deleted. """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


"""===================================================== Course ====================================================="""


class Course(CRUDEntry):
    LEVEL_CHOICES = (
        (1, "1 курс, 1 семестр"),
        (2, "1 курс, 2 семестр"),
        (3, "2 курс, 1 семестр"),
        (4, "2 курс, 2 семестр"),
        (5, "3 курс, 1 семестр"),
        (6, "3 курс, 2 семестр"),
        (7, "4 курс, 1 семестр"),
        (8, "4 курс, 2 семестр"),
    )

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, verbose_name="Уровень")

    comment_set = GenericRelation(Comment, content_type_field='object_type')
    subscription_set = GenericRelation(Subscription, content_type_field='object_type')

    class Meta(CRUDEntry.Meta):
        ordering = ('level',)
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def get_latest_submissions(self):
        return Submission.objects.filter(assignment__isnull=False, problem__contest__course=self)

    def get_discussion_url(self):
        return reverse('contests:course-discussion', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s" % self.title


"""===================================================== Credit ====================================================="""


class CreditManager(models.Manager):
    def create_set(self, owner, course, accounts):
        user_ids = accounts.values_list('user_id', flat=True)
        new_credits = []
        for user_id in user_ids:
            new_credit = Credit(owner_id=owner.id, user_id=user_id, course_id=course.id)
            new_credits.append(new_credit)
        return self.bulk_create(new_credits)


class Credit(CRUDEntry):
    SCORE_CHOICES = (
        (5, "отлично"),
        (4, "хорошо"),
        (3, "удовлетворительно"),
        (2, "неудовлетворительно"),
        (0, "нет оценки"),
    )
    DEFAULT_SCORE = 0

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', verbose_name="Владелец")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")

    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, default=DEFAULT_SCORE, verbose_name="Оценка")

    objects = CreditManager()

    class Meta(CRUDEntry.Meta):
        ordering = ('-course',)
        unique_together = ('user', 'course')
        verbose_name = "Зачет"
        verbose_name_plural = "Зачеты"

    def __str__(self):
        return "Зачет по курсу: %s" % self.course.title


"""===================================================== Lesson ====================================================="""


class Lecture(CRUDEntry):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Содержание")

    class Meta(CRUDEntry.Meta):
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"

    def __str__(self):
        return "%s" % self.title


"""==================================================== Contest ====================================================="""


class Contest(CRUDEntry):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")

    attachment_set = GenericRelation(Attachment, content_type_field='object_type')
    comment_set = GenericRelation(Comment, content_type_field='object_type')
    subscription_set = GenericRelation(Subscription, content_type_field='object_type')

    class Meta(CRUDEntry.Meta):
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"

    @property
    def files(self):
        return [attachment.file.path for attachment in self.attachment_set.all()]

    def get_discussion_url(self):
        return reverse('contests:contest-discussion', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s" % self.title


"""==================================================== Problem ====================================================="""


class Problem(CRUDEntry):
    DIFFICULTY_CHOICES = (
        (0, "Легкая"),
        (1, "Средняя"),
        (2, "Сложная"),
        (3, "Очень сложная")
    )
    DEFAULT_DIFFICULTY = 0
    LANGUAGE_CHOICES = (
        ('C++', "C++"),
        ('C', "C")
    )
    DEFAULT_LANGUAGE = 'C++'
    DEFAULT_TIME_LIMIT = 1
    DEFAULT_MEMORY_LIMIT = 64 * 1024

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, verbose_name="Раздел")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = RichTextUploadingField(verbose_name="Описание")

    number = models.PositiveSmallIntegerField(default=1, verbose_name="Номер")
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=DEFAULT_DIFFICULTY, verbose_name="Сложность")
    language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default=DEFAULT_LANGUAGE, verbose_name="Язык")
    compile_args = models.CharField(max_length=255, blank=True, verbose_name="Параметры компиляции")
    launch_args = models.CharField(max_length=255, blank=True, verbose_name="Параметры запуска")
    time_limit = models.PositiveSmallIntegerField(default=DEFAULT_TIME_LIMIT, verbose_name="Ограничение по времени")
    memory_limit = models.PositiveIntegerField(default=DEFAULT_MEMORY_LIMIT, verbose_name="Ограничение по памяти")
    is_testable = models.BooleanField(default=True, verbose_name="Доступно для тестирования?")

    attachment_set = GenericRelation(Attachment, content_type_field='object_type')
    comment_set = GenericRelation(Comment, content_type_field='object_type')
    subscription_set = GenericRelation(Subscription, content_type_field='object_type')

    class Meta(CRUDEntry.Meta):
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    @property
    def files(self):
        return [attachment.file.path for attachment in self.attachment_set.all()]

    def save(self, *args, **kwargs):
        if self.pk is None:
            max_number = Problem.objects.filter(contest=self.contest).aggregate(models.Max('number')).get('number__max', 0) or 0
            self.number = max_number + 1
        super().save(*args, **kwargs)

    def get_latest_submission_by(self, user):
        try:
            return self.submission_set.filter(owner=user).latest('date_created')
        except ObjectDoesNotExist:
            return None

    def get_tests(self):
        return list(self.iotest_set.all()) + list(self.uttest_set.all()) + list(self.fntest_set.all())

    def test(self, submission, observer):
        state, executions = Status.UN, []
        for test in self.get_tests():
            stats = {}
            try:
                state, stats = test.run(submission.files, observer, self)
            except Exception as e:
                state, stats['exception'] = Status.EX, str(e)
            executions.append((test, stats))
            if state != Status.OK:
                break
        Execution.objects.create_set(submission, executions)
        return state

    def get_discussion_url(self):
        return reverse('contests:problem-discussion', kwargs={'pk': self.pk})

    def __str__(self):
        return "#%i. %s" % (self.number, self.title)


"""==================================================== Solution ===================================================="""


class Solution(CRUDEntry):
    problems = models.ManyToManyField(Problem, verbose_name="Задачи")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    pattern = models.TextField(blank=True, verbose_name="Шаблон")

    class Meta(CRUDEntry.Meta):
        verbose_name = "Решение"
        verbose_name_plural = "Решения"

    def __str__(self):
        return "%s" % self.title


"""===================================================== Tests ======================================================"""


class BasicTest(CRUDEntry):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, verbose_name="Задача")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    compile_args = models.CharField(max_length=255, blank=True, verbose_name="Параметры компиляции")
    compile_args_override = models.BooleanField(default=False, verbose_name="Заменить параметры компиляции из задачи?")
    launch_args = models.CharField(max_length=255, blank=True, verbose_name="Параметры запуска")
    launch_args_override = models.BooleanField(default=False, verbose_name="Заменить параметры запуска из задачи?")

    class Meta(CRUDEntry.Meta):
        abstract = True

    def get_compile_args(self):
        compile_args = self.compile_args.split()
        if self.compile_args_override:
            return compile_args
        else:
            return self.problem.compile_args.split() + compile_args

    def get_launch_args(self):
        launch_args = self.launch_args.split()
        if self.launch_args_override:
            return launch_args
        else:
            return self.problem.launch_args.split() + launch_args

    def __str__(self):
        return "%s" % self.title


class IOTest(BasicTest):
    input = models.TextField(blank=True, verbose_name="Входные данные")
    output = models.TextField(blank=True, verbose_name="Выходные данные")

    class Meta(BasicTest.Meta):
        verbose_name = "IO-тест"
        verbose_name_plural = "IO-тесты"

    def run(self, sources, observer, _):
        root = os.path.dirname(sources[0])
        state, stats = Status.UN, {}
        with Sandbox(root) as sandbox:
            executable = sandbox.path('exe')
            observer.set_progress('Компилируем', 5, 100)
            state = sandbox.compile(sources, executable, language=self.problem.language, args=self.get_compile_args(),
                                    timeout=self.problem.time_limit, stats=stats)
            if state == Status.OK:
                input_file = sandbox.create('input.txt', self.input)
                output_file = sandbox.path('output.txt')
                observer.set_progress('Проверяем', 60, 100)
                state = sandbox.execute(executable, args=[input_file, output_file], timeout=self.problem.time_limit,
                                        stats=stats)
                if state == Status.OK:
                    output = sandbox.read(output_file)
                    if output is None:
                        state = Status.NA
                    elif diff(output, self.output):
                        state = Status.WA
                        stats['test_output'] = output
                    else:
                        stats['test_is_passed'] = True
        return state, stats


class UTTest(BasicTest):
    attachment_set = GenericRelation(Attachment, content_type_field='object_type')

    class Meta(BasicTest.Meta):
        verbose_name = "UT-тест"
        verbose_name_plural = "UT-тесты"

    @property
    def files(self):
        return [attachment.file.path for attachment in self.attachment_set.all()]

    def run(self, sources, observer, _):
        root = os.path.dirname(sources[0])
        state, stats = Status.UN, {}
        with Sandbox(root) as sandbox:
            test_sources = sandbox.fetch(self.files)
            executable = sandbox.path('exe')
            observer.set_progress('Компилируем', 5, 100)
            state = sandbox.compile(sources + test_sources, executable, language=self.problem.language,
                                    args=self.get_compile_args(), timeout=self.problem.time_limit, stats=stats)
            if state == Status.OK:
                observer.set_progress('Проверяем', 60, 100)
                state = sandbox.execute(executable, args=self.get_launch_args(), timeout=self.problem.time_limit,
                                        stats=stats)
                if state == Status.OK:
                    returncode = stats.get('execution_returncode')
                    if returncode != 0:
                        state = Status.TF
                    else:
                        stats['test_is_passed'] = True
        return state, stats


class FNTest(CRUDEntry):
    HANDLER_CHOICES = (
        ('fsm.init', "файловый менеджер: тривиальный"),
        ('fsm.comm', "файловый менеджер: общий"),
        ('fsm.spec', "файловый менеджер: специальный"),
        ('mem.init', "менеджер памяти: тривиальный"),
        ('mem.comm', "менеджер памяти: общий"),
        ('mem.spec', "менеджер памяти: специальный"),
        ('lss.init', "линейные системы: тривиальный"),
        ('lss.main', "линейные системы: основной"),
        ('lss.degn', "линейные системы: вырожденная матрица"),
        ('lss.insl', "линейные системы: несовместная матрица"),
        ('lss.degm', "линейные системы: вырожденный минор"),
        ('evc.init', "собственные значения: тривиальный"),
        ('evc.main', "собственные значения: основной"),
        ('evc.extd', "собственные значения: расширенный"),
    )  # catch choices from problems.modules

    problems = models.ManyToManyField(Problem, verbose_name="Задачи")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    handler = models.CharField(max_length=100, choices=HANDLER_CHOICES, verbose_name="Обработчик")

    class Meta(CRUDEntry.Meta):
        verbose_name = "FN-тест"
        verbose_name_plural = "FN-тесты"

    def run(self, sources, observer, problem):
        module_name, function_name = self.handler.split('.')
        module = importlib.import_module('tools.problems.' + module_name)
        return getattr(module, function_name)(sources, observer, problem, self)

    def __str__(self):
        return "%s" % self.title


"""=================================================== Assignment ==================================================="""


class AssignmentQuerySet(models.QuerySet):
    def rollback_score(self):
        return self.update(score=models.F('score') - 1)

    def to_rollback(self, submissions):
        return self.filter(id__in=submissions.values_list('assignment_id', flat=True), score__gt=3)

    def progress(self):
        naccomplished = self.filter(score__in=[5, 4]).count()
        ntotal = self.count() or 1
        return naccomplished * 100 // ntotal


class AssignmentManager(models.Manager):
    def create_random_set(self, owner, contest, limit_per_user, debts=False):
        """ create random set of assignments with problems of given contest
            aligning their number to limit_per_user for contest.course.level students """
        problem_ids = contest.problem_set.all().values_list('id', flat=True)
        if debts:
            user_ids = (Account.students.enrolled().debtors(contest.course.level).values_list('user_id', flat=True))
        else:
            user_ids = (Account.students.enrolled().filter(level=contest.course.level).values_list('user_id', flat=True))
        for user_id in user_ids:
            assigned_problem_ids = self.filter(
                user_id=user_id,
                problem_id__in=problem_ids
            ).values_list(
                'problem_id',
                flat=True
            )
            problem_id_set = set(problem_ids)
            assigned_problem_id_set = set(assigned_problem_ids)
            if len(assigned_problem_ids) < limit_per_user:
                unassigned_problem_ids = list(problem_id_set - assigned_problem_id_set)
                while unassigned_problem_ids and len(assigned_problem_id_set) < limit_per_user:
                    i = random.randint(0, len(unassigned_problem_ids) - 1)
                    problem_id = unassigned_problem_ids.pop(i)
                    new_assignment = Assignment(
                        owner_id=owner.id,
                        user_id=user_id,
                        problem_id=problem_id
                    )
                    new_assignment.save()
                    assigned_problem_id_set.add(problem_id)


class Assignment(CRUDEntry):
    DEFAULT_SCORE = 0
    DEFAULT_SCORE_MAX = 5
    DEFAULT_SUBMISSION_LIMIT = 10

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', verbose_name="Владелец")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, verbose_name="Задача")

    score = models.PositiveSmallIntegerField(default=DEFAULT_SCORE, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name="Оценка")
    score_max = models.PositiveSmallIntegerField(default=DEFAULT_SCORE_MAX, validators=[MinValueValidator(3), MaxValueValidator(5)], verbose_name="Максимальная оценка", help_text="при прохождении посылкой всех тестов, система автоматической проверки ставит максимальную оценку минус один")
    score_is_locked = models.BooleanField(default=False, verbose_name="Оценка заблокирована", help_text="заблокированная оценка не может быть изменена системой автоматической проверки")
    submission_limit = models.PositiveSmallIntegerField(default=DEFAULT_SUBMISSION_LIMIT, verbose_name="Ограничение количества посылок")
    remark = models.CharField(max_length=255, blank=True, verbose_name="Пометка", help_text="для преподавателей")

    comment_set = GenericRelation(Comment, content_type_field='object_type')
    subscription_set = GenericRelation(Subscription, content_type_field='object_type')

    objects = AssignmentManager.from_queryset(AssignmentQuerySet)()

    class Meta(CRUDEntry.Meta):
        unique_together = ('user', 'problem')
        verbose_name = "Задание"
        verbose_name_plural = "Задания"

    def get_latest_submission(self):
        return self.problem.get_latest_submission_by(self.user)

    def get_submissions(self):  # TODO: use self.submission_set instead
        return self.problem.submission_set.filter(owner_id=self.user.id)

    def update(self, submission):
        if self.score_is_locked:
            return
        score = 2
        if submission.status == 'OK':
            score = self.score_max - 1
        elif self.problem.contest.course.level in (6, 7):
            passed = list(submission.execution_set.values_list('test_is_passed', flat=True).order_by())
            if passed.count(True) in (2, 3, 4):
                score = 3
        if score > self.score:
            self.score = score
            self.save()
            Activity.objects.on_assignment_updated(self)

    def get_discussion_url(self):
        return reverse('contests:assignment-discussion', kwargs={'pk': self.pk})

    def __str__(self):
        return "Задание для %s: %s" % (self.user.account, self.problem)


@receiver(models.signals.post_save, sender=Assignment)
def link_existing_submissions(sender, instance, created, **kwargs):
    """ links existing submissions to newly created `Assignment` object. """
    if created:
        submissions = Submission.objects.filter(assignment__isnull=True, owner=instance.user, problem=instance.problem)
        submissions.update(assignment=instance)


"""=================================================== Submission ==================================================="""


class SubmissionQuerySet(models.QuerySet):
    def rollback_status(self):
        return self.update(status='TR')

    def to_rollback(self, problem_id):
        # TODO: use the following if Django's version is >= 3.0
        # return self.filter(problem_id=problem_id, status__in=['OK', 'TR']).filter(models.Exists(
        #     Credit.objects.filter(user_id=models.OuterRef('owner_id'),
        #                           course_id=models.OuterRef('problem__contest__course_id'),
        #                           score=Credit.DEFAULT_SCORE)
        # ))
        return self.filter(problem_id=problem_id, status__in=['OK', 'TR']).annotate(rollback=models.Exists(
            Credit.objects.filter(user_id=models.OuterRef('owner_id'),
                                  course_id=models.OuterRef('problem__contest__course_id'),
                                  score=Credit.DEFAULT_SCORE)
        )).filter(rollback=True)


class Submission(CRDEntry):
    STATUS_CHOICES = (
        ('OK', "Задача решена"),
        ('TF', "Тест провален"),
        ('TR', "Требуется проверка"),
        ('WA', "Неверный ответ"),
        ('NA', "Ответ отсутствует"),
        ('TL', "Превышено ограничение по времени"),
        ('ML', "Превышено ограничение по памяти"),
        ('CL', "Превышено ограничение по времени компиляции"),
        ('FE', "Ошибка операции с плавающей точкой"),
        ('SF', "Ошибка при работе с памятью"),
        ('RE', "Ошибка выполнения"),
        ('CE', "Ошибка компиляции"),
        ('UE', "Ошибка кодировки"),
        ('PE', "Ошибка комплектации"),
        ('EX', "Неизвестная ошибка"),
        ('UN', "Посылка не проверена")
    )
    DEFAULT_STATUS = 'UN'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, verbose_name="Задача")
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True, verbose_name="Задание")

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=DEFAULT_STATUS, verbose_name="Статус")
    task_id = models.UUIDField(null=True, blank=True, verbose_name="Идентификатор асинхронной задачи")
    moss_to_submissions = models.CharField(max_length=200, null=True, validators=[validate_comma_separated_integer_list],
                                           verbose_name="С посылками MOSS")
    moss_report_url = models.URLField(null=True, verbose_name="Ссылка на отчет MOSS")

    attachment_set = GenericRelation(Attachment, content_type_field='object_type')
    comment_set = GenericRelation(Comment, content_type_field='object_type')
    subscription_set = GenericRelation(Subscription, content_type_field='object_type')

    objects = SubmissionQuerySet.as_manager()

    class Meta(CRDEntry.Meta):
        ordering = ('-date_created',)
        verbose_name = "Посылка"
        verbose_name_plural = "Посылки"

    @property
    def is_ok(self):
        return self.status == 'OK'

    @property
    def is_un(self):
        return self.status == 'UN'

    def moss_to_submissions_list(self):
        return self.moss_to_submissions.split(',')

    @property
    def files(self):
        return [attachment.file.path for attachment in self.attachment_set.all()]

    def get_files_as_zip(self):
        stream = io.BytesIO()
        zip_dirname = str(self.pk)
        with zipfile.ZipFile(stream, 'w') as zip_file:
            for file in self.files:
                _, filename = os.path.split(file)
                zip_path = os.path.join(zip_dirname, filename)
                zip_file.write(file, zip_path)
        return stream.getvalue()

    def inspect(self, observer):
        return Status.OK

    def test(self, observer):
        return self.problem.test(self, observer)

    def update(self, state):
        self.task_id = None
        self.status = str(state)
        self.save()
        self.update_assignment()

    def evaluate(self, user, observer):
        state = self.inspect(observer)
        if state == Status.OK:
            state = self.test(observer)
        self.update(state)

    def update_assignment(self):
        if self.assignment is not None:
            self.assignment.update(self)

    def get_discussion_url(self):
        return self.get_absolute_url()

    def __str__(self):
        return "Посылка от %s к задаче %s" % (self.owner.account, self.problem)


"""=================================================== Execution ===================================================="""


class ExecutionManager(models.Manager):
    def create_set(self, submission, executions):
        self.filter(submission=submission).delete()
        new_executions = []
        for test, stats in executions:
            new_execution = Execution(submission=submission, test_type=ContentType.objects.get_for_model(type(test)),
                                      test_id=test.id, **stats)
            new_executions.append(new_execution)
        return self.bulk_create(new_executions)


class Execution(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, verbose_name="Посылка")
    test_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    test_id = models.PositiveIntegerField()
    test = GenericForeignKey(ct_field='test_type', fk_field='test_id')

    compilation_time = models.FloatField(default=0.0, verbose_name="Время компиляции")
    compilation_command = models.TextField(default="", verbose_name="Команда компиляции")
    compilation_stdout = models.TextField(default="", verbose_name="Вывод компилятора в stdout")
    compilation_stderr = models.TextField(default="", verbose_name="Вывод компилятора в stderr")

    execution_memory = models.PositiveIntegerField(default=0, verbose_name="Использовано памяти")
    execution_time = models.FloatField(default=0.0, verbose_name="Время выполнения")
    execution_command = models.TextField(default="", verbose_name="Команда выполнения")
    execution_returncode = models.IntegerField(default=0, verbose_name="Код возврата")
    execution_stdout = models.TextField(default="", verbose_name="Вывод программы в stdout")
    execution_stderr = models.TextField(default="", verbose_name="Вывод программы в stderr")

    test_is_passed = models.BooleanField(default=False, verbose_name="Тест пройден?")
    test_input = models.TextField(default="", verbose_name="Входные данные")
    test_output = models.TextField(default="", verbose_name="Выходные данные")
    test_output_correct = models.TextField(default="", verbose_name="Верные выходные данные")
    test_summary = models.TextField(default="", verbose_name="Сводка")

    exception = models.TextField(default="", verbose_name="Исключение")

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = ExecutionManager()

    class Meta:
        ordering = ('date_created',)
        verbose_name = "Запуск"
        verbose_name_plural = "Запуски"

    def __str__(self):
        return "Запуск: %s на тесте %s от %s" % (self.submission, self.test, self.date_created)


"""====================================================== Tag ======================================================="""


class Tag(models.Model):
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey(ct_field='object_type')

    class Meta:
        verbose_name = "Метка"
        verbose_name_plural = "Метки"

    def __str__(self):
        return "%s" % self.object


"""===================================================== Event ======================================================"""


class EventQuerySet(models.QuerySet):
    def weekly(self, year, week):
        return self.filter(date_start__iso_year=year, date_start__week=week)


class Event(CRUDEntry):
    TYPE_CHOICES = (
        (1, "Лекция"),
        (2, "Семинар"),
        (3, "Коллоквиум"),
        (4, "Зачет"),
        (5, "Экзамен"),
        (6, "Пересдача"),
        (7, "Семестр"),
    )
    TYPE_DEFAULT = 2

    tutor = models.ForeignKey(User, related_name='responsibility_set', blank=True, null=True, on_delete=models.CASCADE, verbose_name="Преподаватель")

    title = models.CharField(max_length=127, verbose_name="Заголовок")
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=TYPE_DEFAULT, verbose_name="Тип")
    place = models.CharField(max_length=15, blank=True, verbose_name="Место проведения")

    date_start = models.DateTimeField(verbose_name="Дата начала")
    date_end = models.DateTimeField(verbose_name="Дата окончания")

    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Метки")

    objects = EventQuerySet.as_manager()

    class Meta(CRUDEntry.Meta):
        ordering = ('-date_start',)
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def __str__(self):
        return "%s: %s" % (self.get_type_display(), self.title)


"""=================================================== TestSuite ===================================================="""


class TestSuite(CRUDEntry):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, verbose_name="Раздел")
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = RichTextUploadingField(verbose_name="Описание")

    class Meta(CRUDEntry.Meta):
        verbose_name = "Набор тестов"
        verbose_name_plural = "Наборы тестов"

    def test(self, submission, observer):
        state, executions = Status.UN, []
        for test in self.get_tests():
            stats = {}
            try:
                state, stats = test.run(submission.files, observer, self)
            except Exception as e:
                state, stats['exception'] = Status.EX, str(e)
            executions.append((test, stats))
            if state != Status.OK:
                break
        Execution.objects.create_set(submission, executions)
        return state

    def __str__(self):
        return self.title


class Test(CRUDEntry):
    owner = None

    testsuite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, verbose_name="Набор тестов")

    number = models.PositiveSmallIntegerField(default=1, verbose_name="Номер")
    question = RichTextUploadingField(verbose_name="Вопрос")
    right_answer = models.CharField(max_length=250, verbose_name="Правильный ответ")

    class Meta(CRUDEntry.Meta):
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def save(self, *args, **kwargs):
        if self.pk is None:  # ???
            max_number = Test.objects.filter(testsuite=self.testsuite).aggregate(models.Max('number')).get('number__max', 0) or 0
            self.number = max_number + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question


"""============================================== TestSuiteSubmission ==============================================="""


class TestSuiteSubmission(CRUDEntry):
    testsuite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, verbose_name="Набор тестов")

    class Meta(CRUDEntry.Meta):
        verbose_name = "Решение набора тестов"
        verbose_name_plural = "Решения наборов тестов"

    def __str__(self):
        return "Решение набора тестов " + str(self.id)


class TestSubmission(CRUDEntry):
    STATUS_CHOICES = (
        ('OK', "Верный ответ"),
        ('WA', "Неверный ответ"),
        ('UN', "Не проверено")
    )
    DEFAULT_STATUS = 'UN'

    owner = None
    testsuitesubmission = models.ForeignKey(TestSuiteSubmission, on_delete=models.CASCADE, verbose_name="Решение набора тестов")

    number = models.PositiveSmallIntegerField(default=1, verbose_name="Номер")
    answer = models.CharField(max_length=250, verbose_name="Ответ")
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=DEFAULT_STATUS, verbose_name="Статус")

    class Meta(CRUDEntry.Meta):
        verbose_name = "Ответ на тест"
        verbose_name_plural = "Ответы на тесты"

    def test(self):
        test = self.testsuitesubmission.testsuite.test_set.get(number=self.number)
        if self.answer == test.right_answer:
            return 'OK'
        else:
            return 'WA'

    def save(self, *args, **kwargs):
        if self.pk is None:  # ???
            max_number = TestSubmission.objects.filter(testsuitesubmission=self.testsuitesubmission).aggregate(models.Max('number')).get('number__max', 0) or 0
            self.number = max_number + 1

        self.status = self.test()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Ответ на тест " + str(self.id)
