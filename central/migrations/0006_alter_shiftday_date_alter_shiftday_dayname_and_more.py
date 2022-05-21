# Generated by Django 4.0.3 on 2022-05-19 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central', '0005_shifttime_rename_day_shiftday_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shiftday',
            name='date',
            field=models.DateField(verbose_name='Datum'),
        ),
        migrations.AlterField(
            model_name='shiftday',
            name='dayname',
            field=models.SlugField(max_length=15, verbose_name='Dag'),
        ),
        migrations.AlterField(
            model_name='shiftday',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Extra info dag'),
        ),
    ]
