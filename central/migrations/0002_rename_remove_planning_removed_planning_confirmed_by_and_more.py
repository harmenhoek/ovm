# Generated by Django 4.0.3 on 2022-04-03 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('central', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='planning',
            old_name='remove',
            new_name='removed',
        ),
        migrations.AddField(
            model_name='planning',
            name='confirmed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='planning_confirmed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='planning',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='planning_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='planning',
            name='removed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='planning_removed_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='postslug',
            field=models.SlugField(blank=True, max_length=5, null=True, unique=True),
        ),
    ]
