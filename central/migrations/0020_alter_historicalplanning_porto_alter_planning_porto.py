# Generated by Django 4.0.3 on 2023-05-22 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('central', '0019_alter_historicalplanning_porto_alter_planning_porto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalplanning',
            name='porto',
            field=models.ForeignKey(blank=True, db_constraint=False, default=0, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='central.porto', verbose_name='Porto'),
        ),
        migrations.AlterField(
            model_name='planning',
            name='porto',
            field=models.ForeignKey(blank=True, default=0, null=True, on_delete=django.db.models.deletion.SET_NULL, to='central.porto', verbose_name='Porto'),
        ),
    ]
