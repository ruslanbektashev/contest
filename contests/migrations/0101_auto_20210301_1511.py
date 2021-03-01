# Generated by Django 2.2.13 on 2021-03-01 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0100_auto_20210301_1304'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['question__number'], 'verbose_name': 'Решение задачи', 'verbose_name_plural': 'Решения задач'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['number'], 'verbose_name': 'Задача', 'verbose_name_plural': 'Задачи'},
        ),
        migrations.AddField(
            model_name='question',
            name='is_prepared',
            field=models.BooleanField(default=False, verbose_name='Готов?'),
        ),
    ]
