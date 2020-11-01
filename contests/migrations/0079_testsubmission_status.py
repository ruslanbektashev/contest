# Generated by Django 3.0.6 on 2020-10-30 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0078_testsubmission_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='testsubmission',
            name='status',
            field=models.CharField(choices=[('OK', 'Верный ответ'), ('WA', 'Неверный ответ'), ('UN', 'Не проверено')], default='UN', max_length=2, verbose_name='Статус'),
        ),
    ]