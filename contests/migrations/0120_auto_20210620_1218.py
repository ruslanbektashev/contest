# Generated by Django 2.2.13 on 2021-06-20 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0119_merge_20210615_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='footprint',
            field=models.TextField(default='[]'),
        ),
    ]