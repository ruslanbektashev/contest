# Generated by Django 2.0 on 2017-12-30 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20171229_0459'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'ordering': ('user__last_name', 'user__first_name', 'user__id'), 'verbose_name': 'Аккаунт', 'verbose_name_plural': 'Аккаунты'},
        ),
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ('-date_created',), 'verbose_name': 'Действие', 'verbose_name_plural': 'Действия'},
        ),
        migrations.AlterModelOptions(
            name='chat',
            options={'ordering': ('-latest_message__date_created',), 'verbose_name': 'Чат', 'verbose_name_plural': 'Чаты'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-date_created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('-date_created',), 'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
    ]
