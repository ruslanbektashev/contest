# Generated by Django 2.2.13 on 2021-08-11 12:48

from django.db import migrations


def migrate_course_leaders(apps, schema_editor):
    Course = apps.get_model('contests', 'Course')
    CourseLeader = apps.get_model('contests', 'CourseLeader')
    if CourseLeader.objects.exists():
        CourseLeader.objects.all().delete()
    new_course_leaders = []
    for course in Course.objects.all():
        for course_leader in course.leaders.all():
            new_course_leaders.append(CourseLeader(course=course, leader=course_leader))
    CourseLeader.objects.bulk_create(new_course_leaders)


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0125_auto_20210808_1535'),
    ]

    operations = [
        migrations.RunPython(migrate_course_leaders, reverse_code=migrations.RunPython.noop, elidable=True)
    ]
