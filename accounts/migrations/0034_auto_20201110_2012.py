# Generated by Django 2.2.13 on 2020-11-10 17:12

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('accounts', '0033_auto_20201103_1245'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddField(
            model_name='account',
            name='degree',
            field=models.CharField(blank=True, max_length=50, verbose_name='Ученая степень'),
        ),
        migrations.AddField(
            model_name='account',
            name='department',
            field=models.CharField(blank=True, max_length=150, verbose_name='Кафедра'),
        ),
        migrations.AddField(
            model_name='account',
            name='image',
            field=models.ImageField(blank=True, upload_to=accounts.models.account_image_path, verbose_name='Аватар'),
        ),
        migrations.AddField(
            model_name='account',
            name='patronymic',
            field=models.CharField(blank=True, max_length=30, verbose_name='Отчество'),
        ),
        migrations.AddField(
            model_name='account',
            name='position',
            field=models.CharField(blank=True, max_length=100, verbose_name='Должность'),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together={('account', 'object_id', 'object_type')},
        ),
    ]