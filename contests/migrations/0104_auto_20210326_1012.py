# Generated by Django 2.2.13 on 2021-03-26 05:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0103_auto_20210326_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='test',
        ),
        migrations.CreateModel(
            name='TestMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('number', models.PositiveSmallIntegerField(default=1, verbose_name='Номер в наборе')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Question', verbose_name='Задача')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Test', verbose_name='Набор задач')),
            ],
            options={
                'verbose_name': 'Привязка задачи к набору',
                'verbose_name_plural': 'Привязки задач к наборам',
                'unique_together': {('test', 'question'), ('test', 'number')},
            },
        ),
        migrations.AddField(
            model_name='test',
            name='questions',
            field=models.ManyToManyField(through='contests.TestMembership', to='contests.Question', verbose_name='Вопросы'),
        ),
    ]