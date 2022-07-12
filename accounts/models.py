import datetime
import enum
import math
from statistics import mean

from django.apps import apps
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone

from contest.abstract import CRUDEntry
from contest.utils import transliterate

"""==================================================== Faculty ====================================================="""


class FacultyManager(models.Manager):
    def available_for_user(self, user):
        return self.get_queryset().filter(Q(id=user.account.faculty_id) | Q(short_name="МФК")).distinct()


class Faculty(models.Model):
    name = models.CharField(max_length=50, verbose_name="Наименование")
    short_name = models.CharField(max_length=50, verbose_name="Краткое наименование")
    group_name = models.CharField(max_length=50, verbose_name="Наименование группы")
    group_prefix = models.CharField(max_length=5, verbose_name="Префикс группы")

    objects = FacultyManager()

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"

    @property
    def is_interfaculty(self):
        return self.short_name == "МФК"

    def __str__(self):
        return self.short_name


"""==================================================== Account ====================================================="""


class AccountQuerySet(models.QuerySet):
    def reset_password(self):
        credentials = []
        for student in self:
            new_password = User.objects.make_random_password()
            student.user.set_password(new_password)
            student.user.save()
            credentials.append([student.get_full_name(), student.username, new_password])
        return credentials


class StudentQuerySet(AccountQuerySet):
    def enrolled(self):
        return self.filter(enrolled=True)

    def with_credits(self, course):
        Credit = apps.get_model('contests', 'Credit')
        subquery = Credit.objects.filter(course=course, user_id=models.OuterRef('user_id'))
        queryset = self if course.faculty.short_name == "МФК" else self.filter(faculty=course.faculty)
        return (queryset.annotate(credit_id=models.Subquery(subquery.values('id')))
                        .annotate(credit_score=models.Subquery(subquery.values('score'))))

    def with_attendance(self, course, at_datetime):
        Attendance = apps.get_model('contests', 'Attendance')
        subquery = Attendance.objects.filter(course=course, user_id=models.OuterRef('user_id'),
                                             date_from__lte=at_datetime, date_to__gte=at_datetime)
        return self.annotate(attendance_flag=models.Subquery(subquery.values('flag')))

    def allowed(self, course):
        return self.with_credits(course).filter(level__lte=course.level)

    def current(self, course):
        return self.allowed(course).exclude(credit_id=None)

    def debtors(self, course):
        return self.with_credits(course).filter(level__gt=course.level).filter(credit_score__lte=2)

    def level_up(self):
        return self.filter(level__lt=Account.LEVEL_MAX).update(level=models.F('level') + 1)

    def level_down(self):
        return self.filter(level__gt=Account.LEVEL_MIN).update(level=models.F('level') - 1)

    def enroll(self):
        User.objects.filter(id__in=list(self.values_list('user_id', flat=True))).update(is_active=True)
        return self.update(enrolled=True, graduated=False)

    def expel(self):
        User.objects.filter(id__in=list(self.values_list('user_id', flat=True))).update(is_active=False)
        return self.update(enrolled=False, graduated=False)

    def graduate(self):
        User.objects.filter(id__in=list(self.values_list('user_id', flat=True))).update(is_active=False)
        return self.update(enrolled=False, graduated=True)

    def get_distinct_groups(self):
        return self.order_by().values_list('group', flat=True).distinct()


class StaffManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type__gt=1).select_related('user')

    def create_set(self, faculty, level, type, admission_year, names):
        new_users_data, new_accounts, credentials = [], [], []
        for name in names:
            first_name = name[1]
            last_name = name[0]
            patronymic = name[2] if len(name) > 2 else ""
            username = transliterate(last_name.lower())
            if User.objects.filter(username=username).exists():
                username = transliterate(first_name[0].lower()) + username
            if User.objects.filter(username=username).exists():
                raise ValueError("Невозможно зарегистрировать пользователя {}: "
                                 "username {} занято".format(last_name, username))
            password = User.objects.make_random_password()
            new_users_data.append({
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'patronymic': patronymic
            })
        group_name = "Преподаватель" if type > 2 else "Модератор"
        group, _ = Group.objects.get_or_create(name=group_name)
        for new_user_data in new_users_data:
            user = User.objects.create_user(username=new_user_data['username'], password=new_user_data['password'],
                                            first_name=new_user_data['first_name'], last_name=new_user_data['last_name'])
            user.groups.add(group)
            new_account = Account(user_id=user.id, faculty=faculty, patronymic=new_user_data['patronymic'], level=level,
                                  type=type, admission_year=admission_year, enrolled=False)
            new_accounts.append(new_account)
            user_initials = "{} {} {}".format(new_user_data['last_name'], new_user_data['first_name'],
                                              new_user_data['patronymic']).strip()
            credentials.append([user_initials, new_user_data['username'], new_user_data['password']])
        return self.bulk_create(new_accounts), credentials

    def get_leader_queryset(self, faculty):
        leader_queryset = User.objects.filter(groups__name="Преподаватель")
        if faculty.short_name != "МФК":
            leader_queryset = leader_queryset.filter(Q(account__faculty=faculty) | Q(account__faculty__short_name="МФК")).distinct()
        leader_queryset = leader_queryset.order_by('account__faculty__short_name', 'last_name', 'first_name')
        return leader_queryset


class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__groups__name="Студент").select_related('user')

    def create_set(self, faculty, level, admission_year, names):
        group_prefix = transliterate(faculty.group_prefix.lower())
        group_names = ["Студент"]
        groups = []
        if faculty.group_prefix:
            group_names.append(faculty.group_prefix + str(admission_year)[2:])
        for group_name in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            groups.append(group)
        new_accounts, credentials = [], []
        i = 1
        for name in names:
            prefix = 'msu_' + group_prefix + str(admission_year)[2:] + '_'
            suffix = str(i).zfill(2)
            while User.objects.filter(username=prefix + suffix).exists():
                i += 1
                suffix = str(i).zfill(2)
            username = prefix + suffix
            password = User.objects.make_random_password()
            first_name = name[1]
            last_name = name[0]
            patronymic = name[2] if len(name) > 2 else ""
            user = User.objects.create_user(username, password=password, first_name=first_name, last_name=last_name)
            user.groups.add(*groups)
            new_account = Account(user_id=user.id, faculty=faculty, patronymic=patronymic, level=level,
                                  admission_year=admission_year)
            new_accounts.append(new_account)
            user_initials = "{} {} {}".format(last_name, first_name, patronymic).strip()
            credentials.append([user_initials, username, password])
            i += 1
        return self.bulk_create(new_accounts), credentials


def account_image_path(instance, filename):
    return "attachments/{app_label}/{model}/{id}/{filename}".format(app_label=instance._meta.app_label.lower(),
                                                                    model=instance._meta.model_name,
                                                                    id=instance.id,
                                                                    filename=filename)


class Account(models.Model):
    GROUP_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
    )
    GROUP_DEFAULT = 1
    LEVEL_CHOICES = (
        (1, "1 курс, I семестр"),
        (2, "1 курс, II семестр"),
        (3, "2 курс, III семестр"),
        (4, "2 курс, IV семестр"),
        (5, "3 курс, V семестр"),
        (6, "3 курс, VI семестр"),
        (7, "4 курс, VII семестр"),
        (8, "4 курс, VIII семестр"),
    )
    LEVEL_DEFAULT = 1
    LEVEL_MIN = 1
    LEVEL_MAX = 8
    TYPE_CHOICES = (
        (1, 'студент'),
        (2, 'модератор'),
        (3, 'преподаватель'),
    )
    TYPE_DEFAULT = 1
    ADMISSION_YEAR_CHOICES = ((y, y) for y in range(2006, timezone.now().year + 1))
    ADMISSION_YEAR_DEFAULT = timezone.now().year

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING, verbose_name="Факультет")

    patronymic = models.CharField(max_length=30, blank=True, verbose_name="Отчество")
    department = models.CharField(max_length=150, blank=True, verbose_name="Кафедра")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    degree = models.CharField(max_length=50, blank=True, verbose_name="Ученая степень")
    image = models.ImageField(upload_to=account_image_path, blank=True, verbose_name="Аватар")
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=TYPE_DEFAULT, verbose_name="Тип")
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=LEVEL_DEFAULT, verbose_name="Уровень")
    group = models.PositiveSmallIntegerField(choices=GROUP_CHOICES, default=GROUP_DEFAULT, verbose_name="Группа")
    subgroup = models.PositiveSmallIntegerField(choices=GROUP_CHOICES, default=GROUP_DEFAULT, verbose_name="Подгруппа")
    enrolled = models.BooleanField(default=True, verbose_name="Обучается?")
    graduated = models.BooleanField(default=False, verbose_name="Закончил обучение?")
    record_book_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="№ зачетной книжки")
    admission_year = models.PositiveSmallIntegerField(choices=ADMISSION_YEAR_CHOICES, default=ADMISSION_YEAR_DEFAULT,
                                                      verbose_name="Год поступления")

    date_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    staff = StaffManager.from_queryset(AccountQuerySet)()
    students = StudentManager.from_queryset(StudentQuerySet)()

    comments_read = models.ManyToManyField('Comment', blank=True)

    class Meta:
        ordering = ('user__last_name', 'user__first_name', 'user_id')
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    @staticmethod
    def make_group_name(group_prefix, group, level):
        group_suffix = (timezone.now().year - level // 2) % 100
        return "{}{}-{}".format(group_prefix, group, group_suffix)

    @property
    def get_group_name(self):
        return self.make_group_name(self.faculty.group_prefix, self.group, self.level)

    @property
    def is_student(self):
        return self.type == 1  # self.user.groups.filter(name="Студент").exists()

    @property
    def is_moderator(self):
        return self.type == 2  # self.user.groups.filter(name="Модератор").exists()

    @property
    def is_instructor(self):
        return self.type == 3  # self.user.groups.filter(name="Преподаватель").exists()

    @property
    def owner(self):
        return self.user

    @property
    def username(self):
        return self.user.username

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def is_active(self):
        return self.user.is_active

    def get_full_name(self):
        full_name = "{last_name} {first_name} {patronymic}".format(first_name=self.first_name, last_name=self.last_name,
                                                                   patronymic=self.patronymic)
        return full_name.strip() or self.user.username

    def get_short_name(self):
        if self.first_name:
            return "{last_name} {first_name_0}.".format(first_name_0=self.first_name[0],
                                                        last_name=self.last_name).strip()
        else:
            return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def last_login(self):
        return self.user.last_login

    @property
    def date_joined(self):
        return self.user.date_joined

    @property
    def solved_problems_count(self):
        Submission = apps.get_model('contests', 'Submission')
        Assignment = apps.get_model('contests', 'Assignment')
        problem_ids = Submission.objects.filter(owner=self.user).values_list('problem', flat=True).distinct().order_by()
        count = 0
        for problem_id in problem_ids:
            if Submission.objects.filter(owner=self.user, problem_id=problem_id, status='OK').exists() or Assignment.objects.filter(user=self.user, problem_id=problem_id, score__gte=3).exists():
                count += 1
        return count

    def course_credit_score(self, course_id=None):
        credits = self.user.credit_set.exclude(score=0)
        if course_id:
            credits = credits.filter(course=course_id)
        credit_scores = credits.values_list('score', flat=True)
        avg_credit_score = mean(credit_scores) if credit_scores else 0
        return round(avg_credit_score * 20 if 0 < avg_credit_score < 6 else 0)

    def course_submissions_score(self, course_id=None):
        Submission = apps.get_model('contests', 'Submission')
        Assignment = apps.get_model('contests', 'Assignment')
        submissions = Submission.objects.filter(owner=self.user)
        if course_id:
            submissions = submissions.filter(problem__contest__course=course_id)
        problem_ids = submissions.values_list('problem', flat=True).distinct().order_by()
        submissions_scores = []
        for problem_id in problem_ids:
            problem_submissions = Submission.objects.filter(owner=self.user, problem=problem_id)
            success_submissions = problem_submissions.filter(status='OK')
            if success_submissions.exists():
                first_success_submission = success_submissions.order_by('date_created')[0]
                submissions_count = problem_submissions.filter(date_created__lte=first_success_submission.date_created).count()
            else:
                submissions_count = problem_submissions.count() + 1
            assignment = problem_submissions.first().assignment
            submission_limit = assignment.submission_limit if assignment else Assignment.DEFAULT_SUBMISSION_LIMIT
            submissions_score = 100 / math.ceil(submissions_count / submission_limit)
            submissions_scores.append(submissions_score)
        return round(mean(submissions_scores)) if submissions_scores else 0

    @property
    def submissions_score(self):
        return self.course_submissions_score()

    @property
    def score(self):
        return self.course_credit_score()

    def get_absolute_url(self):
        return reverse('accounts:account-detail', kwargs={'pk': self.pk})

    def mark_comments_as_read(self, comments):
        # mark corresponding notifications as read
        # Notification.objects.filter(recipient=self.user, object_type=ContentType.objects.get_for_model(Comment),
        #                             object_id__in=comments.values_list('id', flat=True)).mark_as_read()
        self.comments_read.add(*comments)

    def unread_comments_count(self, obj):
        comments_on_object = obj.comment_set.exclude(author=self.user)
        comments_on_object_read_by_user = self.comments_read.filter(object_type=ContentType.objects.get_for_model(obj),
                                                                    object_id=obj.id).exclude(author=self.user)
        return comments_on_object.count() - comments_on_object_read_by_user.count()

    def __str__(self):
        return self.get_full_name()


"""==================================================== Comment ====================================================="""


class CommentMaxLevelError(ValueError):
    pass


class CommentQuerySet(models.QuerySet):
    def actual(self):
        return self.filter(is_deleted=False)

    def mark_as_deleted(self):
        return self.update(is_deleted=True)


class CommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('author')


class Comment(models.Model):
    MAX_LEVEL = 5
    author = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE, verbose_name="Автор")

    thread_id = models.PositiveIntegerField(default=0, db_index=True)
    parent_id = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1, db_index=True)

    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey(ct_field='object_type')

    text = models.TextField(verbose_name="Текст комментария")

    is_deleted = models.BooleanField(default=False, verbose_name="Удален?")

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    objects = CommentManager.from_queryset(CommentQuerySet)()

    class Meta:
        ordering = ('-thread_id', 'order')
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    @property
    def owner(self):
        return self.author

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if created:
            if not self.parent_id:
                self.parent_id = self.id
                self.thread_id = self.id
            else:
                try:
                    with atomic():
                        self._set_thread()
                except (CommentMaxLevelError, Comment.DoesNotExist) as e:
                    self.delete()
                    raise e
            kwargs["force_insert"] = False
            super().save(*args, **kwargs)
        self._notify_users(created)

    @property
    def related_course(self):
        model = self.object_type.model
        if model == 'course':
            return self.object
        elif model == 'contest':
            return self.object.course
        elif model == 'problem':
            return self.object.contest.course
        elif model == 'assignment' or model == 'submission':
            return self.object.problem.contest.course
        else:
            return None

    def _notify_users(self, created=False):
        course = self.related_course
        if course is not None:
            course_leaders = course.leaders.values_list('id', flat=True)
            action = "оставил" if created else "изменил"
            Notification.objects.notify(course_leaders, subject=self.author, action=action + " комментарий",
                                        object=self, relation="в", reference=self.object)
            if self.id != self.parent_id:
                parent_comment = Comment.objects.get(id=self.parent_id)
                if parent_comment.author != self.author:
                    Notification.objects.notify(parent_comment.author, subject=self.author,
                                                action=action + " ответ на Ваш комментарий", object=self,
                                                relation="в", reference=self.object)

    def _set_thread(self):
        parent = Comment.objects.get(id=self.parent_id)
        if parent.level == self.MAX_LEVEL:
            raise CommentMaxLevelError("No replies allowed for this comment")
        self.thread_id = parent.thread_id
        self.level = parent.level + 1
        thread = Comment.objects.filter(thread_id=parent.thread_id)
        thread_tail = thread.filter(level__lte=parent.level, order__gt=parent.order)
        if thread_tail.count():
            min_order = thread_tail.aggregate(models.Min('order'))['order__min']
            thread.filter(order__gte=min_order).update(order=models.F('order') + 1)
            self.order = min_order
        else:
            max_order = thread.aggregate(models.Max('order'))['order__max']
            self.order = max_order + 1

    def soft_delete(self, delete_threads=False, commit=True):
        thread = Comment.objects.filter(thread_id=self.thread_id)
        if self.thread_id == self.id:
            comments_to_delete = thread
        else:
            next_subthread_head = thread.filter(level__lte=self.level, order__gt=self.order).first()
            if next_subthread_head:
                comments_to_delete = thread.filter(order__gte=self.order, order__lt=next_subthread_head.order)
            else:
                comments_to_delete = thread.filter(order__gte=self.order)
        if commit and (delete_threads or comments_to_delete.count() == 1):
            comments_to_delete.update(is_deleted=True)
        return comments_to_delete.count()

    def is_repliable(self):
        return self.level < self.MAX_LEVEL

    def get_absolute_url(self):
        return reverse(
            'contests:{object_type}-{view_name}'.format(
                object_type=self.object_type.model,
                view_name='detail' if self.object_type.model == 'submission' else 'discussion'
            ),
            kwargs={'pk': self.object_id}
        ) + '#comment_{comment_id}'.format(comment_id=self.pk)

    def __str__(self):
        return f"Комментарий {self.pk}"


"""================================================== Announcement =================================================="""


class AnnouncementQuerySet(models.QuerySet):
    def actual(self):
        return self.filter(actual__gte=timezone.now().today())

    def proper_group(self, user):
        if not user.has_perm('accounts.change_announcement'):
            return self.filter(Q(group__in=user.groups.all()) | Q(group=None))
        else:
            return self.all()


class Announcement(CRUDEntry):
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Для группы")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст объявления")
    actual = models.DateField(null=True, blank=True, verbose_name="Актуально до")

    objects = AnnouncementQuerySet.as_manager()

    @property
    def group_name(self):
        if self.group is None:
            return 'Для всех'
        else:
            return self.group

    class Meta(CRUDEntry.Meta):
        ordering = ('-date_created',)
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)
        if self.group is not None:
            action = "добавил объявление" if created else "изменил объявление"
            Notification.objects.notify(self.group, subject=self.owner, action=action, object=self)

    def __str__(self):
        return self.title


"""================================================== Notification =================================================="""


class NotificationQuerySet(models.QuerySet):
    def actual(self):
        return self.filter(is_deleted=False)

    def unread(self):
        return self.actual().filter(is_read=False)

    def mark_as_deleted(self):
        return self.actual().update(is_deleted=True)

    def mark_as_read(self):
        return self.unread().update(is_read=True)


class NotificationManager(models.Manager):
    class Recipients(enum.Enum):
        COURSE_LEADERS = 1

    def notify(self, recipients, subject, action, object=None, relation=None, reference=None, date_created=None):
        if isinstance(recipients, str):
            group = Group.objects.get(name=recipients)
            recipient_ids = group.user_set.all().values_list('id', flat=True)
        elif isinstance(recipients, Group):
            recipient_ids = recipients.user_set.all().values_list('id', flat=True)
        elif isinstance(recipients, models.QuerySet) or isinstance(recipients, list):
            recipient_ids = recipients
        elif isinstance(recipients, User):
            recipient_ids = [recipients.id]
        else:
            raise ValueError
        optional = dict()
        if relation:
            optional['relation'] = relation
        if date_created:
            optional['date_created'] = date_created
        new_notifications = []
        for recipient_id in recipient_ids:
            if isinstance(subject, User) and subject.id == recipient_id:
                continue
            notification = Notification(subject_type=ContentType.objects.get_for_model(subject),
                                        subject_id=subject.id,
                                        recipient_id=recipient_id,
                                        action=action,
                                        **optional)
            if object:
                notification.object_type = ContentType.objects.get_for_model(object)
                notification.object_id = object.id
            if reference:
                notification.reference_type = ContentType.objects.get_for_model(reference)
                notification.reference_id = reference.id
            new_notifications.append(notification)
        self.bulk_create(new_notifications)


class Notification(models.Model):
    recipient = models.ForeignKey(User, related_name='notifications', verbose_name="Получатель", on_delete=models.CASCADE)
    subject_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    subject_id = models.PositiveIntegerField()
    subject = GenericForeignKey(ct_field='subject_type', fk_field='subject_id')
    object_type = models.ForeignKey(ContentType, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey(ct_field='object_type')
    reference_type = models.ForeignKey(ContentType, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    reference_id = models.PositiveIntegerField(blank=True, null=True)
    reference = GenericForeignKey(ct_field='reference_type', fk_field='reference_id')

    action = models.CharField(max_length=255, verbose_name="Описание действия")
    relation = models.CharField(max_length=255, blank=True, verbose_name="Описание связи")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано?")
    is_deleted = models.BooleanField(default=False, verbose_name="Удалено?")

    date_created = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    objects = NotificationManager.from_queryset(NotificationQuerySet)()

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Оповещение"
        verbose_name_plural = "Оповещения"

    def __str__(self):
        context = {
            'recipient': self.recipient.account,
            'action': self.action,
            'object': '',
            'slash': '',
            'relation': '',
            'reference': ''
        }
        if self.object:
            context['object'] = self.object
        if self.reference:
            context['slash'] = ' / '
            context['reference'] = self.reference
        if self.relation:
            context['relation'] = " {} ".format(self.relation)
        if isinstance(self.subject, User):
            context['subject'] = self.subject.last_name
        else:
            context['subject'] = self.subject
        return "{subject} {action} {object}{slash}{relation}{reference}".format(**context)
