# Generated by Django 2.2.13 on 2021-08-07 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0050_auto_20210726_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='subgroup',
            field=models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2')], default=1, verbose_name='Подгруппа'),
        ),
    ]
