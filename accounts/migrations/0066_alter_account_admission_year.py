# Generated by Django 3.2.16 on 2023-04-10 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0065_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='admission_year',
            field=models.PositiveSmallIntegerField(choices=[(2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023)], default=2023, verbose_name='Год поступления'),
        ),
    ]
