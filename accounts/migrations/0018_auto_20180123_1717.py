# Generated by Django 2.0.1 on 2018-01-23 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20180118_1449'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='date_modified',
            new_name='date_updated',
        ),
        migrations.AlterField(
            model_name='account',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(0, 'отчислен'), (1, '1 курс, 1 семестр'), (2, '1 курс, 2 семестр'), (3, '2 курс, 1 семестр'), (4, '2 курс, 2 семестр'), (5, '3 курс, 1 семестр'), (6, '3 курс, 2 семестр'), (7, '4 курс, 1 семестр'), (8, '4 курс, 2 семестр'), (9, 'выпускник'), (10, 'преподаватель')], default=1, verbose_name='Уровень'),
        ),
        migrations.AlterField(
            model_name='account',
            name='since',
            field=models.PositiveSmallIntegerField(choices=[(2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018)], default=2018, verbose_name='Год поступления'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='action',
            field=models.CharField(max_length=255, verbose_name='Действие'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Удалено?'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Прочитано?'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(1, 'журнальное'), (2, 'информационное'), (3, 'предупреждение'), (4, 'важное'), (5, 'критическое')], default=2, verbose_name='Уровень'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group', verbose_name='Для группы'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='text',
            field=models.TextField(verbose_name='Текст объявления'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='latest_message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.Message', verbose_name='Последнее сообщение'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Удален?'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(verbose_name='Текст комментария'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='message',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Удалено?'),
        ),
        migrations.AlterField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Прочитано?'),
        ),
        migrations.AlterField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL, verbose_name='Получатель'),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL, verbose_name='Отправитель'),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(verbose_name='Текст сообщения'),
        ),
    ]
