# Generated by Django 2.2.25 on 2022-04-02 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0137_auto_20220317_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='score_is_locked',
            field=models.BooleanField(default=False, help_text='заблокированная оценка не может быть изменена системой автоматической проверки', verbose_name='Заблокировать оценку'),
        ),
        migrations.AlterField(
            model_name='option',
            name='is_correct',
            field=models.BooleanField(default=False, verbose_name='Верный'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='is_testable',
            field=models.BooleanField(default=True, verbose_name='Разрешить автоматическую проверку решений'),
        ),
    ]