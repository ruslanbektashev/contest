# Generated by Django 2.0.1 on 2018-01-05 03:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('accounts', '0014_auto_20180104_0328'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group'),
        ),
    ]
