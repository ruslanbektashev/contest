# Generated by Django 2.2.13 on 2021-07-13 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0120_auto_20210620_1218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='title',
            new_name='title_official',
        ),
    ]
