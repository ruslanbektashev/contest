from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone

from contest.abstract import CRUDEntry

"""==================================================== Account ====================================================="""


class AccountQuerySet(models.QuerySet):
    def reset_password(self):
        credentials = []
        for student in self:
            new_password = User.objects.make_random_password()
            student.user.set_password(new_password)
            student.user.save()
            credentials.append([student.last_name, student.first_name, student.username, new_password])
        return credentials


class StudentQuerySet(AccountQuerySet):
    def enrolled(self):
        return self.filter(enrolled=True)

    def with_credits(self):
        from contests.models import Credit
        return self.annotate(
            credit_id=models.Subquery(Credit.objects.filter(course__level=models.OuterRef('level'),
                                                            user_id=models.OuterRef('user_id')).values('id'))
        ).annotate(
            credit_score=models.Subquery(Credit.objects.filter(course__level=models.OuterRef('level'),
                                                               user_id=models.OuterRef('user_id')).values('score'))
        )

    def none_credits(self):
        from contests.models import Credit
        return self.annotate(
            has_credit=models.Exists(Credit.objects.filter(course__level=models.OuterRef('level'),
                                                           user_id=models.OuterRef('user_id')))
        ).filter(has_credit=False)

    def debtors(self, level):
        from contests.models import Credit
        return self.filter(~models.Q(level=level)).annotate(
            credit_id=models.Subquery(Credit.objects.filter(course__level=level,
                                                            user_id=models.OuterRef('user_id')).values('id'))
        ).annotate(
            credit_score=models.Subquery(Credit.objects.filter(course__level=level,
                                                               user_id=models.OuterRef('user_id')).values('score'))
        ).filter(credit_score__lte=2)

    def level_up(self):
        return self.update(level=models.F('level') + 1)

    def level_down(self):
        return self.update(level=models.F('level') - 1)

    def enroll(self):
        return self.update(enrolled=True, graduated=False)

    def expel(self):
        return self.update(enrolled=False, graduated=False)

    def graduate(self):
        return self.update(enrolled=False, graduated=True)


class StaffManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type__gt=1).select_related('user')

    def create_set(self, level, type, admission_year, names):
        alphabet_ru_a = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        alphabet_ru_s = 'жйхцчшщыюя'
        translit_en_a = 'abvgdee_zi_klmnoprstuf________e__'
        translit_en_s = ['zh', 'y', 'kh', 'ts', 'ch', 'sh', 'sh', 'y', 'yu', 'ya']
        transtable = {ord(c): p for c, p in zip(alphabet_ru_a, translit_en_a)}
        transtable.update({ord(c): p for c, p in zip(alphabet_ru_s, translit_en_s)})
        new_accounts, credentials = [], []
        for name in names:
            first_name = name[1].lower()
            last_name = name[0].lower()
            username = last_name.translate(transtable)
            if User.objects.filter(username=username).exists():
                username = first_name[0].translate(transtable) + username
            password = User.objects.make_random_password()
            user = User.objects.create_user(username, password=password, first_name=first_name.capitalize(),
                                            last_name=last_name.capitalize())
            group_name = "Преподаватель" if type > 2 else "Модератор"
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            new_account = Account(user_id=user.id, level=level, type=type, admission_year=admission_year, enrolled=False)
            new_accounts.append(new_account)
            credentials.append([name[0], name[1], username, password])
        return self.bulk_create(new_accounts), credentials


class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=1).select_related('user')

    def create_set(self, level, admission_year, names):
        new_accounts, credentials = [], []
        i = 1
        for name in names:
            prefix = 'msu_' + str(admission_year) + '_'
            suffix = str(i).zfill(2)
            while User.objects.filter(username=prefix + suffix).exists():
                i += 1
                suffix = str(i).zfill(2)
            username = prefix + suffix
            password = User.objects.make_random_password()
            first_name = name[1].lower().capitalize()
            last_name = name[0].lower().capitalize()
            user = User.objects.create_user(username, password=password, first_name=first_name, last_name=last_name)
            for group_name in ('Студент', 'M' + str(admission_year)[2:]):
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
            new_account = Account(user_id=user.id, level=level, admission_year=admission_year)
            new_accounts.append(new_account)
            credentials.append([name[0], name[1], username, password])
            i += 1
        return self.bulk_create(new_accounts), credentials


def account_image_path(instance, filename):
    return "attachments/{app_label}/{model}/{id}/{filename}".format(app_label=instance._meta.app_label.lower(),
                                                                    model=instance._meta.model_name,
                                                                    id=instance.id,
                                                                    filename=filename)


class Account(models.Model):
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
    LEVEL_DEFAULT = 1
    TYPE_CHOICES = (
        (1, 'студент'),
        (2, 'модератор'),
        (3, 'преподаватель'),
    )
    TYPE_DEFAULT = 1
    ADMISSION_YEAR_CHOICES = ((y, y) for y in range(2006, timezone.now().year + 1))
    ADMISSION_YEAR_DEFAULT = timezone.now().year

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    patronymic = models.CharField(max_length=30, blank=True, verbose_name="Отчество")
    department = models.CharField(max_length=150, blank=True, verbose_name="Кафедра")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    degree = models.CharField(max_length=50, blank=True, verbose_name="Ученая степень")
    image = models.ImageField(upload_to=account_image_path, blank=True, verbose_name="Аватар")
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=LEVEL_DEFAULT, verbose_name="Уровень")
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=TYPE_DEFAULT, verbose_name="Тип")
    admission_year = models.PositiveSmallIntegerField(choices=ADMISSION_YEAR_CHOICES, default=ADMISSION_YEAR_DEFAULT,
                                                      verbose_name="Год поступления")
    enrolled = models.BooleanField(default=True, verbose_name="Обучается?")
    graduated = models.BooleanField(default=False, verbose_name="Закончил обучение?")

    date_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    staff = StaffManager.from_queryset(AccountQuerySet)()
    students = StudentManager.from_queryset(StudentQuerySet)()

    comments_read = models.ManyToManyField('Comment')

    class Meta:
        ordering = ('user__last_name', 'user__first_name', 'user_id')
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

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

    def get_absolute_url(self):
        return reverse('accounts:account-detail', kwargs={'pk': self.pk})

    def mark_comments_as_read(self, comments):
        self.comments_read.add(*comments)

    def unread_comments_count(self, obj):
        comments_on_object = obj.comment_set.exclude(author=self.user)
        comments_on_object_read_by_user = self.comments_read.filter(object_type=ContentType.objects.get_for_model(obj),
                                                                    object_id=obj.id).exclude(author=self.user)
        return comments_on_object.count() - comments_on_object_read_by_user.count()

    def __str__(self):
        return self.get_full_name()


"""================================================== Subscription =================================================="""


class Subscription(models.Model):
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey(ct_field='object_type')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('user', 'object_id', 'object_type')

    def __str__(self):
        return '%s, %s: %s' % (self.user.account.get_full_name(), self.object_type.model, self.object.title)


"""==================================================== Activity ===================================================="""


def make_activities(recipients, subject, action, object=None, reference=None, level=None, date_created=None):
    if isinstance(recipients, Group):
        recipient_ids = recipients.user_set.all().values_list('id', flat=True)
    elif isinstance(recipients, models.QuerySet) or isinstance(recipients, list):
        recipient_ids = recipients
    else:
        recipient_ids = [recipients.id]
    optional = dict()
    if level:
        optional['level'] = level
    if date_created:
        optional['date_created'] = date_created
    new_activities = []
    for recipient_id in recipient_ids:
        activity = Activity(subject_type=ContentType.objects.get_for_model(subject),
                            subject_id=subject.id,
                            recipient_id=recipient_id,
                            action=action,
                            **optional)
        if object:
            activity.object_type = ContentType.objects.get_for_model(object)
            activity.object_id = object.id
        if reference:
            activity.reference_type = ContentType.objects.get_for_model(reference)
            activity.reference_id = reference.id
        new_activities.append(activity)
    return new_activities


class ActivityQuerySet(models.QuerySet):
    def actual(self):
        return self.filter(is_deleted=False)

    def unread(self):
        return self.actual().filter(is_read=False)

    def mark_as_deleted(self):
        return self.actual().update(is_deleted=True)

    def mark_as_read(self):
        return self.unread().update(is_read=True)


class ActivityManager(models.Manager):
    def notify_group(self, group_name, **kwargs):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return
        new_activities = make_activities(group, **kwargs)
        self.bulk_create(new_activities)

    def notify_user(self, username, **kwargs):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return
        new_activities = make_activities(user, **kwargs)
        self.bulk_create(new_activities)

    def notify_users(self, users, **kwargs):
        new_activities = make_activities(users, **kwargs)
        self.bulk_create(new_activities)

    def on_assignment_updated(self, assignment):
        pass

    def on_submission_created(self, submission):
        if submission.problem.contest.course.level in (6, 7):
            self.notify_user('sbr',
                             subject=submission.owner, action="отправил решение задачи", object=submission.problem,
                             level=2)


class Activity(models.Model):
    LEVEL_CHOICES = (
        (1, "журнальное"),
        (2, "информационное"),
        (3, "предупреждение"),
        (4, "важное"),
        (5, "критическое")
    )
    DEFAULT_LEVEL = 2

    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    subject_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    subject_id = models.PositiveIntegerField()
    subject = GenericForeignKey(ct_field='subject_type', fk_field='subject_id')
    object_type = models.ForeignKey(ContentType, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object = GenericForeignKey(ct_field='object_type')
    reference_type = models.ForeignKey(ContentType, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    reference_id = models.PositiveIntegerField(blank=True, null=True)
    reference = GenericForeignKey(ct_field='reference_type', fk_field='reference_id')

    action = models.CharField(max_length=255, verbose_name="Действие")
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=DEFAULT_LEVEL, verbose_name="Уровень")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано?")
    is_deleted = models.BooleanField(default=False, verbose_name="Удалено?")

    date_created = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    objects = ActivityManager.from_queryset(ActivityQuerySet)()

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Действие"
        verbose_name_plural = "Действия"

    def __str__(self):
        context = {
            'recipient': self.recipient.account,
            'action': self.action,
            'object': '',
            'slash': '',
            'reference': ''
        }
        if self.object:
            context['object'] = self.object
        if self.reference:
            context['slash'] = ' / '
            context['reference'] = self.reference
        if isinstance(self.subject, User):
            context['subject'] = self.subject.last_name
        else:
            context['subject'] = self.subject
        return "{subject} {action} {object}{slash}{reference}".format(**context)


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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
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

    def soft_delete(self):
        thread = Comment.objects.filter(thread_id=self.thread_id)
        if self.thread_id == self.id:
            thread.update(is_deleted=True)
        else:
            next_subthread_head = thread.filter(level__lte=self.level, order__gt=self.order).first()
            if next_subthread_head:
                thread.filter(order__gte=self.order, order__lt=next_subthread_head.order).update(is_deleted=True)
            else:
                thread.filter(order__gte=self.order).update(is_deleted=True)

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
        return "Комментарий {}".format(self.pk)


"""==================================================== Message ====================================================="""


class MessageQuerySet(models.QuerySet):
    def actual(self):
        return self.filter(is_deleted=False)

    def unread(self):
        return self.actual().filter(is_read=False)

    def mark_as_deleted(self, user):
        return self.actual().filter(sender=user).update(is_deleted=True)

    def mark_as_read(self, user):
        return self.unread().filter(recipient=user).update(is_read=True)

    def get_messages(self, user_a, user_b):
        return self.filter(models.Q(sender=user_a, recipient=user_b) | models.Q(sender=user_b, recipient=user_a))


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE, verbose_name="Отправитель")
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE,
                                  verbose_name="Получатель")

    text = models.TextField(verbose_name="Текст сообщения")

    is_read = models.BooleanField(default=False, verbose_name="Прочитано?")
    is_deleted = models.BooleanField(default=False, verbose_name="Удалено?")

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = MessageQuerySet.as_manager()

    class Meta:
        ordering = ('-date_created',)
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        context = {
            'text': self.text[:100],
            'dots': '',
        }
        if len(self.text) > 100:
            context['dots'] = '...'
        return "{text}{dots}".format(**context)


"""====================================================== Chat ======================================================"""


class ChatQuerySet(models.QuerySet):
    def actual(self, user):
        return self.filter(models.Q(user_a=user) | models.Q(user_b=user))

    def update_or_create_chat(self, user_one, user_two, latest_message):
        user_a, user_b = sorted((user_one, user_two), key=lambda user: user.id)
        return Chat.objects.update_or_create(
            user_a=user_a,
            user_b=user_b,
            defaults={
                'latest_message': latest_message
            }
        )


class Chat(models.Model):
    user_a = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    user_b = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    # TODO: consider replacing by property
    latest_message = models.ForeignKey(Message, related_name='+', on_delete=models.CASCADE,
                                       verbose_name="Последнее сообщение")

    objects = ChatQuerySet.as_manager()

    class Meta:
        unique_together = ('user_a', 'user_b')
        ordering = ('-latest_message__date_created',)
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def get_messages(self):
        return Message.objects.get_messages(self.user_a, self.user_b)

    def __str__(self):
        return "Диалог %s с %s" % (self.user_a.account, self.user_b.account)


"""================================================== Announcement =================================================="""


class Announcement(CRUDEntry):
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Для группы")

    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст объявления")

    class Meta(CRUDEntry.Meta):
        ordering = ('-date_created',)
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return "%s" % self.title
