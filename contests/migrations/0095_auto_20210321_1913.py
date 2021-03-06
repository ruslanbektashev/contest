# Generated by Django 2.2.13 on 2021-03-21 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0094_auto_20210320_2309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ('question__number',), 'verbose_name': 'Решение задачи', 'verbose_name_plural': 'Решения задач'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('number',), 'verbose_name': 'Задача', 'verbose_name_plural': 'Задачи'},
        ),
        migrations.AlterField(
            model_name='answer',
            name='test_submission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contests.TestSubmission', verbose_name='Решение набора задач'),
        ),
        migrations.AlterField(
            model_name='question',
            name='test',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contests.Test', verbose_name='Набор задач'),
        ),
        migrations.AlterField(
            model_name='testsubmission',
            name='score',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Оценка'),
        ),
    ]
