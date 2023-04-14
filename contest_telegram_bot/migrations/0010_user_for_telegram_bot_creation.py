from django.db import migrations


def create_user_for_telegram_bot(apps, schema_editor):
    group_model = apps.get_model('auth', 'Group')
    group = group_model.objects.create(name='Бот')
    group.save()

    user_model = apps.get_model('auth', 'User')
    user = user_model.objects.create_user(username='telegram_bot', first_name='Телеграм-бот')
    user.groups.add(group)
    user.save()

    faculty_model = apps.get_model('accounts', 'Faculty')

    account_model = apps.get_model('accounts', 'Account')
    account = account_model.objects.create(user=user, faculty=faculty_model.objects.get(short_name='МФК'))
    account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contest_telegram_bot', '0009_rename_problems_mark_telegramusersettings_assignments_mark'),
    ]

    operations = [
        migrations.RunPython(create_user_for_telegram_bot, migrations.RunPython.noop, elidable=True)
    ]
