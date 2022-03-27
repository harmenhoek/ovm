# Generated by Django 4.0.3 on 2022-03-27 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('central', '0005_planning_confirmed_planning_remove'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='bug', help_text='Set a icon from <a target="_blank" href="https://fontawesome.com/icons?m=free">this library</a>.', max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='flag_comment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='flag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='central.flag'),
        ),
    ]
