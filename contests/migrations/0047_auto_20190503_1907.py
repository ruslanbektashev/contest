# Generated by Django 2.1.4 on 2019-05-03 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0046_auto_20190503_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('pattern', models.TextField(blank=True, verbose_name='Шаблон')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
                ('problems', models.ManyToManyField(to='contests.Problem', verbose_name='Задачи')),
            ],
            options={
                'ordering': ('date_created',),
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='fntest',
            name='pattern',
        ),
    ]
