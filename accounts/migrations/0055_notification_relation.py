# Generated by Django 2.2.13 on 2021-11-14 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0054_auto_20211114_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='relation',
            field=models.CharField(blank=True, max_length=255, verbose_name='Описание связи'),
        ),
    ]