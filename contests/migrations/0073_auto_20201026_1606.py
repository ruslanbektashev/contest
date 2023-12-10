# Generated by Django 3.0.6 on 2020-10-26 11:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '0072_remove_test_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='right_answer',
            field=models.CharField(max_length=250, verbose_name='Правильный ответ'),
        ),
        migrations.CreateModel(
            name='TestSuiteSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
                ('testsuite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.TestSuite', verbose_name='Набор тестов')),
            ],
            options={
                'verbose_name': 'Решение набора тестов',
                'verbose_name_plural': 'Решения наборов тестов',
                'ordering': ('date_created',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('answer', models.CharField(max_length=250, verbose_name='Ответ')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
                ('testsuitesubmission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.TestSuiteSubmission', verbose_name='Ответ')),
            ],
            options={
                'verbose_name': 'Ответ на тест',
                'verbose_name_plural': 'Ответы на тесты',
                'ordering': ('date_created',),
                'abstract': False,
            },
        ),
    ]
