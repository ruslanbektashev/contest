# Generated by Django 2.1.2 on 2018-11-13 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0033_assignment_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='is_testable',
            field=models.BooleanField(default=True, verbose_name='Доступно для тестирования?'),
        ),
    ]
