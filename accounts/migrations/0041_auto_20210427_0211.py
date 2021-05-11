# Generated by Django 2.2.13 on 2021-04-26 23:11

from django.db import migrations


def create_faculties(apps, schema_editor):
    Faculty = apps.get_model('accounts', 'Faculty')
    f1 = Faculty.objects.create(name="Прикладная Математика и Информатика")
    f2 = Faculty.objects.create(name="Психология")
    Account = apps.get_model('accounts', 'Account')
    Account.objects.update(faculty=f1)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0040_auto_20210427_0211'),
    ]

    operations = [
        migrations.RunPython(create_faculties, migrations.RunPython.noop)
    ]