# Generated by Django 2.2.25 on 2022-03-13 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0134_auto_20220221_0121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='status',
            field=models.CharField(choices=[('OK', 'Задача решена'), ('PS', 'Задача решена частично'), ('TF', 'Тест провален'), ('TR', 'Требуется проверка'), ('WA', 'Неверный ответ'), ('NA', 'Ответ отсутствует'), ('TL', 'Превышено ограничение по времени'), ('ML', 'Превышено ограничение по памяти'), ('CL', 'Превышено ограничение по времени компиляции'), ('FE', 'Ошибка операции с плавающей точкой'), ('SF', 'Ошибка при работе с памятью'), ('RE', 'Ошибка выполнения'), ('CE', 'Ошибка компиляции'), ('UE', 'Ошибка кодировки'), ('PE', 'Ошибка комплектации'), ('EX', 'Неизвестная ошибка'), ('EV', 'Посылка проверяется'), ('UN', 'Посылка не проверена')], default='UN', max_length=2, verbose_name='Статус'),
        ),
    ]
