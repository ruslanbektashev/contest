# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-06 11:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0016_auto_20170405_1651'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unittest',
            old_name='command',
            new_name='args',
        ),
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('EX', 'Отлично'), ('GO', 'Хорошо'), ('SA', 'Удовлетворительно'), ('PO', 'Неудовлетворительно'), ('UN', 'Нет посылок')], default='UN', max_length=2),
        ),
    ]
