# Generated by Django 2.2.24 on 2021-11-27 19:17

from django.db import migrations


def revoke_login_permission_from_non_enrolled_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(account__enrolled=False, account__type=1).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0055_notification_relation'),
    ]

    operations = [
        migrations.RunPython(revoke_login_permission_from_non_enrolled_users, migrations.RunPython.noop, elidable=True)
    ]
