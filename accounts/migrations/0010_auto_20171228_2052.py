# Generated by Django 2.0 on 2017-12-28 17:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20171224_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='latest_message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='accounts.Message'),
        ),
    ]
