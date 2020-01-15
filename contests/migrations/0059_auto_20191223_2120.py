# Generated by Django 2.2.5 on 2019-12-23 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0058_auto_20191003_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.CharField(choices=[('OK', 'Задача решена'), ('TF', 'Тест провален'), ('WA', 'Неверный ответ'), ('NA', 'Ответ отсутствует'), ('TL', 'Превышено ограничение по времени'), ('ML', 'Превышено ограничение по памяти'), ('FE', 'Ошибка операции с плавающей точкой'), ('SF', 'Ошибка при работе с памятью'), ('RE', 'Ошибка выполнения'), ('CE', 'Ошибка компиляции'), ('UE', 'Ошибка кодировки'), ('PE', 'Ошибка комплектации'), ('EX', 'Неизвестная ошибка'), ('UN', 'Посылка не проверена')], default='UN', max_length=2, verbose_name='Статус'),
        ),
    ]