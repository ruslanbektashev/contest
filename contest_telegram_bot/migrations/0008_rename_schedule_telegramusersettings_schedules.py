# Generated by Django 3.2.18 on 2023-04-10 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest_telegram_bot', '0007_alter_telegramusersettings_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='telegramusersettings',
            old_name='schedule',
            new_name='schedules',
        ),
    ]
