import json
from accounts.models import Account, Comment
from datetime import datetime
import os
from contest.settings import BASE_DIR


ACCOUNTS_PATH = 'additional_tools/accounts_new.json'
COMMENTS_PATH = 'additional_tools/comments_new.json'


def compare_accounts_json():
    file_path = os.path.join(BASE_DIR, ACCOUNTS_PATH)
    with open(file_path) as file:
        s = file.read()
    accounts = json.loads(s)

    file_path = os.path.join(BASE_DIR, 'additional_tools/accounts.json')
    with open(file_path) as file:
        s = file.read()
    accounts_old = json.loads(s)
    for acc, acc_old in zip(accounts, accounts_old):
        assert acc['old_id'] == acc_old['old_id']
        assert acc['username'] == acc_old['username']
        assert acc['first_name'] == acc_old['first_name']
        assert acc['last_name'] == acc_old['last_name']
        assert acc['email'] == acc_old['email']
        assert acc['admission_year'] == acc_old['admission_year']


def get_accounts_json():
    accounts = list()
    for account in Account.objects.filter(old_id__isnull=False):
        if account.old_id not in {
            2,  # Павел Алисейчик
            158,  # Юрий Шуткин
            253,  # Станислав Чиревко
            222,  # Сергей Родин
            160,  # Дмитрий Алексеев
            168,  # Кирилл Голиков
            272,  # Наталья Дейнека
            162,  # Александр Петюшко
            275,  # Руслан Бекташев
        }:
            accounts.append({
                'old_id': account.old_id,
                'username': account.username,
                'password': account.user.password,
                'first_name': account.user.first_name,
                'last_name': account.user.last_name,
                'email': account.user.email,
                'admission_year': account.admission_year,
            })
    s = json.dumps(accounts)
    file_path = os.path.join(BASE_DIR, ACCOUNTS_PATH)
    with open(file_path, 'w+') as file:
        file.write(s)


def get_comments_json():
    comments = list()
    for comment in Comment.objects.filter(old_id__isnull=False):
        comments.append({
            'old_id': comment.old_id,
            'author': Account.objects.get(user=comment.author).old_id,
            'thread_id': Comment.objects.get(id=comment.thread_id).old_id,
            'parent_id': Comment.objects.get(id=comment.parent_id).old_id,
            'level': comment.level,
            'order': comment.order,
            'object_type': comment.object_type.model,
            'object_id': comment.object_id,
            'text': comment.text,
            'is_deleted': comment.is_deleted,
            'date_created': [datetime.timestamp(comment.date_created), str(comment.date_created)],
        })
    comments.sort(key=lambda x: x['date_created'][0], reverse=True)
    for i in range(len(comments)):
        comments[i]['date_created'] = comments[i]['date_created'][1]
    s = json.dumps(comments)
    file_path = os.path.join(BASE_DIR, COMMENTS_PATH)
    with open(file_path, 'w+') as file:
        file.write(s)
