# Generated by Django 2.1.4 on 2019-05-04 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0047_auto_20190503_1907'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='solution',
            options={'ordering': ('date_created',), 'verbose_name': 'Решение', 'verbose_name_plural': 'Решения'},
        ),
        migrations.AddField(
            model_name='assignment',
            name='score',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Оценка'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='score_max',
            field=models.PositiveSmallIntegerField(default=5, verbose_name='Максимальная оценка'),
        ),
    ]
