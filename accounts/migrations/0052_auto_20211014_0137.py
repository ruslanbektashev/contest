# Generated by Django 2.2.24 on 2021-10-13 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_account_subgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(1, '1 курс, I семестр'), (2, '1 курс, II семестр'), (3, '2 курс, III семестр'), (4, '2 курс, IV семестр'), (5, '3 курс, V семестр'), (6, '3 курс, VI семестр'), (7, '4 курс, VII семестр'), (8, '4 курс, VIII семестр')], default=1, verbose_name='Уровень'),
        ),
    ]
