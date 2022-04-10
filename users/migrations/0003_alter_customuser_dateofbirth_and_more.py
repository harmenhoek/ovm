# Generated by Django 4.0.3 on 2022-04-03 18:36

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_customuser_active_delete_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='dateofbirth',
            field=models.DateField(blank=True, null=True, verbose_name='Geboortedatum'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='Telefoonnummer in formaat +31612065956.', max_length=128, null=True, region=None, unique=True, verbose_name='Telefoonnummer'),
        ),
    ]
