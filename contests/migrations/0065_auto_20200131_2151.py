# Generated by Django 2.2.5 on 2020-01-31 18:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0064_assignment_score_is_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='remark',
            field=models.CharField(blank=True, help_text='для преподавателей', max_length=255, verbose_name='Пометка'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='score',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Оценка'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='score_is_locked',
            field=models.BooleanField(default=False, help_text='заблокированная оценка не может быть изменена системой автоматической проверки', verbose_name='Оценка заблокирована'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='score_max',
            field=models.PositiveSmallIntegerField(default=5, help_text='при прохождении посылкой всех тестов, система автоматической проверки ставит максимальную оценку минус один', validators=[django.core.validators.MinValueValidator(3), django.core.validators.MaxValueValidator(5)], verbose_name='Максимальная оценка'),
        ),
    ]
