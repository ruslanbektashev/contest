# Generated by Django 2.2.13 on 2021-06-13 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0117_auto_20210505_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='deadline',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Принимать посылки до'),
        ),
    ]
