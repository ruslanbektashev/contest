# Generated by Django 2.2.13 on 2020-12-04 11:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0084_merge_20201126_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='leaders',
            field=models.ManyToManyField(limit_choices_to={'account__type': 3}, related_name='courses_leading', to=settings.AUTH_USER_MODEL, verbose_name='Ведущие'),
        ),
    ]
