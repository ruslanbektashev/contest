# Generated by Django 2.2.5 on 2019-10-03 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0057_remove_execution_owner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='credit',
            options={'ordering': ('-course',), 'verbose_name': 'Зачет', 'verbose_name_plural': 'Зачеты'},
        ),
    ]
