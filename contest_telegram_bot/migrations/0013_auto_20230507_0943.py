# Generated by Django 3.2.18 on 2023-05-07 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest_telegram_bot', '0012_auto_20230501_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramusersettings',
            name='announcements',
            field=models.BooleanField(default=True, verbose_name='Объявления'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='assignments',
            field=models.BooleanField(default=True, verbose_name='Назначение задач'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='assignments_mark',
            field=models.BooleanField(default=True, verbose_name='Оценки за задачи'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='comments',
            field=models.BooleanField(default=True, verbose_name='Комментарии'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='courses_mark',
            field=models.BooleanField(default=True, verbose_name='Оценки за курсы'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='questions',
            field=models.BooleanField(default=True, verbose_name='Вопросы'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='reports',
            field=models.BooleanField(default=True, verbose_name='Сообщения об ошибках'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='schedules',
            field=models.BooleanField(default=False, verbose_name='Расписание'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='submissions',
            field=models.BooleanField(default=False, verbose_name='Отправленные посылки'),
        ),
        migrations.AlterField(
            model_name='telegramusersettings',
            name='submissions_mark',
            field=models.BooleanField(default=True, verbose_name='Оценки за посылки'),
        ),
    ]
