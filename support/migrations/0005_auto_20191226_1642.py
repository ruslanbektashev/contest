# Generated by Django 2.2.5 on 2019-12-26 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('support', '0004_report'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ('-date_created',), 'verbose_name': 'Отчет об ошибке', 'verbose_name_plural': 'Отчеты об ошибках'},
        ),
        migrations.RemoveField(
            model_name='report',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='report',
            name='sending_time',
        ),
        migrations.AddField(
            model_name='report',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='report',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата изменения'),
        ),
        migrations.AddField(
            model_name='report',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='text',
            field=models.TextField(blank=True, verbose_name='Отчет'),
        ),
    ]
