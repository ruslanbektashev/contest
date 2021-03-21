# Generated by Django 2.2.13 on 2021-03-20 19:35

from django.db import migrations


def update_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    SubmissionPattern = apps.get_model('contests', 'SubmissionPattern')
    submission_pattern_content_type = ContentType.objects.get_for_model(SubmissionPattern)
    submission_pattern_permissions = Permission.objects.filter(content_type_id=submission_pattern_content_type).order_by('id')
    submission_pattern_permissions.filter(codename__endswith='solution').delete()
    new_permissions = [
        {'name': "Добавлять Шаблон посылки", 'codename': "add_submission_pattern"},
        {'name': "Изменять Шаблон посылки", 'codename': "change_submission_pattern"},
        {'name': "Удалять Шаблон посылки", 'codename': "delete_submission_pattern"},
        {'name': "Просматривать Шаблон посылки", 'codename': "view_submission_pattern"},
    ]
    for submission_pattern_permission, new_permission in zip(submission_pattern_permissions, new_permissions):
        submission_pattern_permission.name = new_permission['name']
        submission_pattern_permission.codename = new_permission['codename']
        submission_pattern_permission.save(update_fields=['name', 'codename'])


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0092_auto_20210320_2048'),
    ]

    operations = [
        migrations.RunPython(update_permissions, reverse_code=migrations.RunPython.noop)
    ]
