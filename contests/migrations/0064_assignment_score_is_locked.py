# Generated by Django 2.2.5 on 2020-01-31 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0063_auto_20200127_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='score_is_locked',
            field=models.BooleanField(default=False, verbose_name='Оценка заблокирована'),
        ),
    ]