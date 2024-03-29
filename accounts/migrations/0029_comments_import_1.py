# Generated by Django 2.2.12 on 2020-05-16 15:00
import json
import os
import sys

from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db import migrations, models

COMMENTS_PATH = 'additional_tools/comments.json'


def ensure_permissions_exist(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def import_comments(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    Comment = apps.get_model('accounts', 'Comment')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    Comment.objects.all().delete()

    file_path = os.path.join(settings.BASE_DIR, COMMENTS_PATH)
    with open(file_path) as file:
        s = file.read()
    comments = json.loads(s)
    authors = {}
    content_types = {}
    new_comments = []
    for comment in comments:
        if comment['author'] not in authors:
            authors[comment['author']] = Account.objects.get(old_id=comment['author']).user
        if comment['object_type'] not in content_types:
            content_types[comment['object_type']] = ContentType.objects.get(model=comment['object_type'])
        new_comments.append(Comment(
            old_id=comment['old_id'],
            author=authors[comment['author']],
            thread_id=comment['thread_id'],
            parent_id=comment['parent_id'],
            level=comment['level'],
            order=comment['order'],
            object_type=content_types[comment['object_type']],
            object_id=comment['object_id'],
            text=comment['text'],
            is_deleted=False,
            date_created=comment['date_created']
        ))
    new_comments = list(reversed(new_comments))
    Comment.objects.bulk_create(new_comments)


def delete_comments(apps, schema_editor):
    Comment = apps.get_model('accounts', 'Comment')
    MAX_OLD_ID = 10000
    Comment.objects.filter(old_id__isnull=False, old_id__lt=MAX_OLD_ID).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_comments_backup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date_created',
            field=models.DateTimeField(auto_now_add=False, verbose_name='Дата создания'),
        ),
        migrations.RunPython(ensure_permissions_exist, migrations.RunPython.noop, elidable=True),
        migrations.RunPython(import_comments, delete_comments, elidable=True)
    ] if 'test' not in sys.argv[1:] else []
