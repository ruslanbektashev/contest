# Generated by Django 2.2.13 on 2021-03-01 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0097_auto_20210226_1128'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ('date_created',), 'verbose_name': 'Решение задачи', 'verbose_name_plural': 'Решения задач'},
        ),
        migrations.AddField(
            model_name='answer',
            name='is_right',
            field=models.BooleanField(default=False, verbose_name='Правильный?'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='options',
            field=models.ManyToManyField(blank=True, to='contests.Option', verbose_name='Выбранные варианты'),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('test_submission', 'question')},
        ),
    ]
