# Generated by Django 2.1.4 on 2019-05-07 23:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0002_auto_20181113_2249'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='faq',
            options={'ordering': ('-date_created',), 'verbose_name': 'FAQ', 'verbose_name_plural': 'FAQ'},
        ),
    ]
