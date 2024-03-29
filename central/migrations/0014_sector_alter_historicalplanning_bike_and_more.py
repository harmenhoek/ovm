# Generated by Django 4.0.3 on 2023-05-06 11:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('central', '0013_alter_historicalplanning_bike_alter_planning_bike'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('shortcut', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='bug', help_text='Set a icon from <a target="_blank" href="https://fontawesome.com/icons?m=free">this library</a>.', max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='historicalplanning',
            name='bike',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Fietsnummer'),
        ),
        migrations.AlterField(
            model_name='historicalplanning',
            name='porto',
            field=models.BooleanField(default=False, verbose_name='Portofoon'),
        ),
        migrations.AlterField(
            model_name='planning',
            name='bike',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Fietsnummer'),
        ),
        migrations.AlterField(
            model_name='planning',
            name='porto',
            field=models.BooleanField(default=False, verbose_name='Portofoon'),
        ),
        migrations.CreateModel(
            name='HistoricalSector',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('shortcut', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='bug', help_text='Set a icon from <a target="_blank" href="https://fontawesome.com/icons?m=free">this library</a>.', max_length=100)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical sector',
                'verbose_name_plural': 'historical sectors',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name='historicalpost',
            name='sector',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='central.sector'),
        ),
        migrations.AddField(
            model_name='post',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='central.sector'),
        ),
    ]
