# Generated by Django 3.2.16 on 2023-04-08 10:49

from django.db import migrations


def replace_wrappers(instance):
    opening_wrappers = instance.description.count(r"\\(")
    closing_wrappers = instance.description.count(r"\\)")
    if opening_wrappers > 0 and opening_wrappers == closing_wrappers:
        instance.description = instance.description.replace(r"\\(", r"\(")
        instance.description = instance.description.replace(r"\\)", r"\)")
        instance.save()


def fix_mathjax_inline_wrappers(apps, schema_editor):
    Course = apps.get_model('contests', 'Course')
    for course in Course.objects.filter(title_official__contains="Практикум на ЭВМ."):
        for contest in course.contest_set.all():
            replace_wrappers(contest)
            for problem in contest.problem_set.all():
                replace_wrappers(problem)


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0142_auto_20230330_1552'),
    ]

    operations = [
        migrations.RunPython(fix_mathjax_inline_wrappers, migrations.RunPython.noop, elidable=True)
    ]
