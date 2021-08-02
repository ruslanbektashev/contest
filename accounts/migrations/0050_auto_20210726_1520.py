# Generated by Django 2.2.13 on 2021-07-26 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0049_account_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='faculty',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='accounts.Faculty', verbose_name='Факультет'),
            preserve_default=False,
        ),
    ]