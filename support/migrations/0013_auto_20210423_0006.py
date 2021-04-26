# Generated by Django 2.2.13 on 2021-04-22 19:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0012_auto_20210422_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='addressee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Адресат'),
        ),
    ]