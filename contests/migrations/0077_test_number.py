# Generated by Django 3.0.6 on 2020-10-30 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0076_remove_test_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Номер'),
        ),
    ]
