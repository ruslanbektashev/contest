# Generated by Django 2.2.24 on 2021-12-12 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0129_auto_20211014_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execution',
            name='date_created',
            field=models.DateTimeField(verbose_name='Дата создания'),
        ),
    ]