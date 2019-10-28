# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-13 11:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0018_auto_20170409_0248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='credit',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='credit',
            unique_together=set([('user', 'course')]),
        ),
    ]
