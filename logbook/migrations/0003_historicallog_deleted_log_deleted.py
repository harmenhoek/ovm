# Generated by Django 4.0.3 on 2022-05-20 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0002_alter_log_file1_alter_log_file2_historicallog'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicallog',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='log',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
