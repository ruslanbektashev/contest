# Generated by Django 3.2.16 on 2023-03-06 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest_telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='chat_id',
            field=models.BigIntegerField(verbose_name='ID телеграм-сущности'),
        ),
    ]
