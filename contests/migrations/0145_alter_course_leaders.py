# Generated by Django 3.2.18 on 2023-05-03 20:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0144_alter_submission_problem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='leaders',
            field=models.ManyToManyField(related_name='courses_leading', through='contests.CourseLeader', to=settings.AUTH_USER_MODEL, verbose_name='Ведущие преподаватели'),
        ),
    ]
