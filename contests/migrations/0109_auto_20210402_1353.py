# Generated by Django 2.2.13 on 2021-04-02 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0108_auto_20210329_1530'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testmembership',
            options={'ordering': ('number',), 'verbose_name': 'Привязка задачи к набору', 'verbose_name_plural': 'Привязки задач к наборам'},
        ),
    ]