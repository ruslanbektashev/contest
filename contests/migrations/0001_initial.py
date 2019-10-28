# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-08 00:44
from __future__ import unicode_literals

import contests.misc
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_limit', models.PositiveSmallIntegerField(default=10, verbose_name='Ограничение по посылкам')),
                ('is_accomplished', models.BooleanField(default=False, verbose_name='Задание выполнено?')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Задание',
                'verbose_name_plural': 'Задания',
            },
        ),
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('start_date', models.DateTimeField(verbose_name='Дата начала')),
                ('end_date', models.DateTimeField(verbose_name='Дата окончания')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Контест',
                'verbose_name_plural': 'Контесты',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('level', models.PositiveSmallIntegerField(verbose_name='Уровень')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Курс',
                'verbose_name_plural': 'Курсы',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.PositiveSmallIntegerField(null=True, verbose_name='Оценка')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Course', verbose_name='Курс')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credits', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Зачет',
                'verbose_name_plural': 'Зачеты',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='IOTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Номер')),
                ('input', models.TextField(verbose_name='Входные данные')),
                ('output', models.TextField(verbose_name='Выходные данные')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Тест задачи',
                'verbose_name_plural': 'Тесты задачи',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Course', verbose_name='Курс')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Лекция',
                'verbose_name_plural': 'Лекции',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='LessonAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.FileField(upload_to=contests.misc.lesson_attachment_path, verbose_name='Файл')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Lesson', verbose_name='Лекция')),
            ],
            options={
                'verbose_name': 'Файл лекции',
                'verbose_name_plural': 'Файлы лекции',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Номер')),
                ('description', models.TextField(verbose_name='Описание')),
                ('difficulty', models.PositiveSmallIntegerField(choices=[(0, 'Легко'), (1, 'Средне'), (2, 'Сложно'), (3, 'Вызов')], default=0, verbose_name='Сложность')),
                ('time_limit', models.PositiveSmallIntegerField(default=1, verbose_name='Ограничение по времени')),
                ('memory_limit', models.PositiveIntegerField(default=65536, verbose_name='Ограничение по памяти')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Contest', verbose_name='Контест')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
                'ordering': ['creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('UN', 'Не определен'), ('OK', 'Задача решена'), ('WA', 'Неверный ответ'), ('NA', 'Нет ответа'), ('CE', 'Ошибка компиляции'), ('RE', 'Ошибка времени выполнения'), ('FE', 'Ошибка операций с плавающей точкой'), ('SF', 'Ошибка при работе с памятью'), ('TL', 'Превышено ограничение по времени'), ('ML', 'Превышен ограничение по памяти')], default='UN', max_length=2, verbose_name='Статус')),
                ('elapsed_time', models.FloatField(null=True, verbose_name='Затрачено времени')),
                ('memory_usage', models.PositiveIntegerField(null=True, verbose_name='Затрачено памяти')),
                ('compilation_log', models.TextField(null=True, verbose_name='Отчет компилятора')),
                ('evaluation_log', models.TextField(null=True, verbose_name='Вывод программы')),
                ('difference', models.TextField(null=True, verbose_name='Разность ответов')),
                ('passed_tests', models.PositiveIntegerField(null=True, verbose_name='Пройдено тестов')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('failed_test', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contests.IOTest', verbose_name='Проваленный тест')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача')),
            ],
            options={
                'verbose_name': 'Посылка',
                'verbose_name_plural': 'Посылки',
                'ordering': ['-creation_date'],
            },
        ),
        migrations.CreateModel(
            name='SubmissionAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.FileField(upload_to=contests.misc.submission_attachment_path, verbose_name='Файл')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Submission', verbose_name='Посылка')),
            ],
            options={
                'verbose_name': 'Файл посылки',
                'verbose_name_plural': 'Файлы посылки',
                'ordering': ['creation_date'],
            },
        ),
        migrations.AddField(
            model_name='iotest',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
        ),
        migrations.AddField(
            model_name='contest',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Course', verbose_name='Курс'),
        ),
        migrations.AddField(
            model_name='contest',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='latest_submission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contests.Submission', verbose_name='Последняя посылка'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together=set([('user', 'problem')]),
        ),
    ]
