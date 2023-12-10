# Generated by Django 2.2.5 on 2019-12-23 18:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('support', '0003_auto_20190508_0244'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('text', models.TextField(blank=True, verbose_name='Отчёт')),
                ('sending_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время отправки')),
                ('page_url', models.URLField(verbose_name='Откуда отправлено')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
            ],
        ),
    ]
