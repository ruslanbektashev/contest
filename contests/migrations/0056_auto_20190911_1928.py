# Generated by Django 2.2.5 on 2019-09-11 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0054_submission_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='assignment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contests.Assignment', verbose_name='Задание'),
        ),
    ]
