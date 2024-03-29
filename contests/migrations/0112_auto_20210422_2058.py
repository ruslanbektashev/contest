# Generated by Django 2.2.13 on 2021-04-22 17:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0111_filter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='option',
            options={},
        ),
        migrations.RemoveField(
            model_name='option',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='option',
            name='date_updated',
        ),
        migrations.RemoveField(
            model_name='option',
            name='is_right',
        ),
        migrations.RemoveField(
            model_name='option',
            name='question',
        ),
        migrations.AddField(
            model_name='option',
            name='is_correct',
            field=models.BooleanField(default=False, verbose_name='Верный?'),
        ),
        migrations.AddField(
            model_name='option',
            name='problem',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Задача'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='problem',
            name='score_for_3',
            field=models.PositiveSmallIntegerField(default=50, verbose_name='Баллов для 3'),
        ),
        migrations.AddField(
            model_name='problem',
            name='score_for_4',
            field=models.PositiveSmallIntegerField(default=75, verbose_name='Баллов для 4'),
        ),
        migrations.AddField(
            model_name='problem',
            name='score_for_5',
            field=models.PositiveSmallIntegerField(default=90, verbose_name='Баллов для 5'),
        ),
        migrations.AddField(
            model_name='problem',
            name='score_max',
            field=models.PositiveSmallIntegerField(default=100, verbose_name='Максимальная оценка в баллах'),
        ),
        migrations.AddField(
            model_name='problem',
            name='type',
            field=models.CharField(choices=[('Program', 'Способ ответа: программа'), ('Text', 'Способ ответа: текст'), ('Files', 'Способ ответа: файлы'), ('Options', 'Способ ответа: варианты'), ('Test', 'Тест')], default='Program', max_length=8, verbose_name='Тип'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submission',
            name='main_submission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_submissions', to='contests.Submission', verbose_name='Подпосылки'),
        ),
        migrations.AddField(
            model_name='submission',
            name='options',
            field=models.ManyToManyField(to='contests.Option', verbose_name='Варианты ответа'),
        ),
        migrations.AddField(
            model_name='submission',
            name='score',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Оценка в баллах'),
        ),
        migrations.AddField(
            model_name='submission',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='Текст ответа'),
        ),
        migrations.CreateModel(
            name='SubProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(default=1, verbose_name='Номер в тесте')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Problem', verbose_name='Тест')),
                ('sub_problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contests.Problem', verbose_name='Задача')),
            ],
            options={
                'verbose_name': 'Подзадача теста',
                'verbose_name_plural': 'Подзадачи теста',
                'ordering': ('number',),
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='sub_problems',
            field=models.ManyToManyField(through='contests.SubProblem', to='contests.Problem', verbose_name='Подзадачи'),
        ),
        migrations.AddConstraint(
            model_name='subproblem',
            constraint=models.UniqueConstraint(fields=('problem', 'sub_problem'), name='unique_sub_problem_in_problem'),
        ),
    ]
