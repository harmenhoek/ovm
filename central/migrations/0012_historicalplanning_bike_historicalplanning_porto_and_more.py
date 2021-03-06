# Generated by Django 4.0.3 on 2022-06-03 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central', '0011_historicalplanning_external_planning_external'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalplanning',
            name='bike',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='historicalplanning',
            name='porto',
            field=models.BooleanField(default=False, verbose_name='Heeft een porto'),
        ),
        migrations.AddField(
            model_name='planning',
            name='bike',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='planning',
            name='porto',
            field=models.BooleanField(default=False, verbose_name='Heeft een porto'),
        ),
    ]
