# Generated by Django 3.0.6 on 2020-10-11 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0068_auto_20201005_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
    ]
