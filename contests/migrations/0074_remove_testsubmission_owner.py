# Generated by Django 3.0.6 on 2020-10-26 12:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0073_auto_20201026_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testsubmission',
            name='owner',
        ),
    ]
