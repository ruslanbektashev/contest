# Generated by Django 3.2.18 on 2023-04-10 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest_telegram_bot', '0006_telegramusersettings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='telegramusersettings',
            options={'verbose_name': 'Настройки телеграм-пользователя'},
        ),
    ]
