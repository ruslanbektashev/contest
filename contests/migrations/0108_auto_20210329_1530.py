# Generated by Django 2.2.13 on 2021-03-29 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0107_auto_20210328_1857'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ('question__number',), 'permissions': [('check_answer', 'Проверять Решение задачи')], 'verbose_name': 'Решение задачи', 'verbose_name_plural': 'Решения задач'},
        ),
    ]