# Generated by Django 2.2.13 on 2021-06-14 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0117_auto_20210505_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='footprint',
            field=models.TextField(blank=True, null=True),
        ),
    ]
