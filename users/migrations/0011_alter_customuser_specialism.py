# Generated by Django 4.0.3 on 2022-05-22 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_historicaluserspecialism_colorcode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='specialism',
            field=models.ManyToManyField(blank=True, help_text='See Bootstrap colors: https://getbootstrap.com/docs/5.0/utilities/colors/', to='users.userspecialism'),
        ),
    ]
