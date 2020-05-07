# Generated by Django 3.0.5 on 2020-05-04 07:41

from django.db import migrations
from django.contrib.auth.models import User
import json
import os
from contest.settings import BASE_DIR


ACCOUNTS_PATH = 'additional_tools/accounts.json'


def import_accounts(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')

    ids = {
        # actual id : old id
        109: 131,  # Станислав Чиревко
        312: 142,  # Наталья Дейнека
        206: 83,  # Дмитрий Алексеев
        209: 90,  # Кирилл Голиков
        52: 2,  # Павел Алисейчик
        314: 85,  # Александр Петюшко
        203: 118,  # Сергей Родин
        53: 82,  # Юрий Шуткин
        1: 144,  # Бекташев Руслан
    }
    for actual_id, old_id in ids.items():
        user = User.objects.get(id=actual_id)
        account = Account.objects.get(user=user.id)
        account.old_id = old_id
        account.save()

    file_path = os.path.join(BASE_DIR, ACCOUNTS_PATH)
    with open(file_path) as file:
        s = file.read()
    accounts = json.loads(s)
    new_accounts = list()
    for account in accounts:
        user = User.objects.create_user(
            username=account['username'],
            password=account['password'],
            first_name=account['first_name'],
            last_name=account['last_name'],
            email=account['email']
        )
        new_accounts.append(Account(
            user_id=user.id,
            old_id=account['old_id'],
            enrolled=account['enrolled'],
            graduated=account['graduated'],
            level=account['level'],
            admission_year=account['admission_year']
        ))
    Account.objects.bulk_create(new_accounts)


def delete_users(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    file_path = os.path.join(BASE_DIR, ACCOUNTS_PATH)
    with open(file_path) as file:
        s = file.read()
    accounts = json.loads(s)
    old_ids = list(map(lambda x: x['old_id'], accounts))
    users_ids = Account.objects.filter(old_id__in=old_ids).values_list('user_id')
    User.objects.filter(id__in=users_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_auto_20200504_2313'),
    ]

    operations = [
        migrations.RunPython(import_accounts, delete_users)
    ]
