# Generated by Django 2.0.1 on 2018-01-23 14:17

import contests.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0030_auto_20180118_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Содержание')),
            ],
            options={
                'verbose_name': 'Лекция',
                'verbose_name_plural': 'Лекции',
                'ordering': ('date_created',),
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Метка', 'verbose_name_plural': 'Метки'},
        ),
        migrations.AlterField(
            model_name='assignment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='result',
            field=models.CharField(choices=[('EX', 'Отлично'), ('GO', 'Хорошо'), ('SA', 'Удовлетворительно'), ('PO', 'Неудовлетворительно'), ('UN', 'Нет посылок')], default='UN', max_length=2, verbose_name='Результат'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='submission_limit',
            field=models.PositiveSmallIntegerField(default=10, verbose_name='Ограничение количества посылок'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Студент'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(upload_to=contests.models.attachment_path, verbose_name='Файл'),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Course', verbose_name='Курс'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='course',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='course',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='course',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(1, '1 курс, 1 семестр'), (2, '1 курс, 2 семестр'), (3, '2 курс, 1 семестр'), (4, '2 курс, 2 семестр'), (5, '3 курс, 1 семестр'), (6, '3 курс, 2 семестр'), (7, '4 курс, 1 семестр'), (8, '4 курс, 2 семестр')], verbose_name='Уровень'),
        ),
        migrations.AlterField(
            model_name='course',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Course', verbose_name='Курс'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='score',
            field=models.PositiveSmallIntegerField(choices=[(5, 'отлично'), (4, 'хорошо'), (3, 'удовлетворительно'), (2, 'неудовлетворительно'), (0, 'нет оценки')], default=0, verbose_name='Оценка'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Студент'),
        ),
        migrations.AlterField(
            model_name='event',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='event',
            name='date_end',
            field=models.DateTimeField(verbose_name='Дата окончания'),
        ),
        migrations.AlterField(
            model_name='event',
            name='date_start',
            field=models.DateTimeField(verbose_name='Дата начала'),
        ),
        migrations.AlterField(
            model_name='event',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='event',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='event',
            name='place',
            field=models.CharField(blank=True, max_length=15, verbose_name='Место проведения'),
        ),
        migrations.AlterField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(blank=True, to='contests.Tag', verbose_name='Метки'),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=127, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='event',
            name='tutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responsibility_set', to=settings.AUTH_USER_MODEL, verbose_name='Преподаватель'),
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Лекция'), (2, 'Семинар'), (3, 'Коллоквиум'), (4, 'Зачет'), (5, 'Экзамен'), (6, 'Пересдача'), (7, 'Семестр')], default=2, verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='compilation_stderr',
            field=models.TextField(blank=True, verbose_name='Вывод компилятора в stderr'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='compilation_stdout',
            field=models.TextField(blank=True, verbose_name='Вывод компилятора в stdout'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='compilation_time',
            field=models.FloatField(blank=True, verbose_name='Время компиляции'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='execution_memory',
            field=models.PositiveIntegerField(blank=True, verbose_name='Использовано памяти'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='execution_stderr',
            field=models.TextField(blank=True, verbose_name='Вывод программы в stderr'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='execution_stdout',
            field=models.TextField(blank=True, verbose_name='Вывод программы в stdout'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='execution_time',
            field=models.FloatField(blank=True, verbose_name='Время выполнения'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='output',
            field=models.TextField(blank=True, verbose_name='Выходные данные'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='passed',
            field=models.BooleanField(verbose_name='Пройден?'),
        ),
        migrations.AlterField(
            model_name='execution',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Submission', verbose_name='Посылка'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='input',
            field=models.TextField(blank=True, verbose_name='Входные данные'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='output',
            field=models.TextField(blank=True, verbose_name='Выходные данные'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='iotest',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='contest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Contest', verbose_name='Раздел'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='difficulty',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Легко'), (1, 'Средне'), (2, 'Тяжело'), (3, 'Вызов')], default=0, verbose_name='Сложность'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='language',
            field=models.CharField(choices=[('C++', 'C++'), ('C', 'C')], default='C++', max_length=8, verbose_name='Язык'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='memory_limit',
            field=models.PositiveIntegerField(default=65536, verbose_name='Ограничение по памяти'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Номер'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='time_limit',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Ограничение по времени'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.CharField(choices=[('OK', 'Задача решена'), ('WA', 'Неверный ответ'), ('TF', 'Тест провален'), ('NA', 'Ответ отсутствует'), ('CE', 'Ошибка компиляции'), ('RE', 'Ошибка выполнения'), ('FE', 'Ошибка операций с плавающей точкой'), ('SF', 'Ошибка при работе с памятью'), ('TL', 'Превышено ограничение по времени'), ('ML', 'Превышено ограничение по памяти'), ('UN', 'Задача не проверена')], default='UN', max_length=2, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='uttest',
            name='args',
            field=models.CharField(blank=True, max_length=255, verbose_name='Параметры запуска'),
        ),
        migrations.AlterField(
            model_name='uttest',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='uttest',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AlterField(
            model_name='uttest',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='uttest',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='uttest',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Заголовок'),
        ),
        migrations.DeleteModel(
            name='Lesson',
        ),
        migrations.AddField(
            model_name='lecture',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Course', verbose_name='Курс'),
        ),
        migrations.AddField(
            model_name='lecture',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
    ]
