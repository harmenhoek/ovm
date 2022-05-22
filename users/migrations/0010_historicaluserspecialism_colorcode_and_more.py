# Generated by Django 4.0.3 on 2022-05-22 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_rename_historicaluserspecialisms_historicaluserspecialism_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluserspecialism',
            name='colorcode',
            field=models.CharField(default='secondary', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userspecialism',
            name='colorcode',
            field=models.CharField(default='secondary', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='specialism',
            field=models.ManyToManyField(blank=True, to='users.userspecialism'),
        ),
    ]
