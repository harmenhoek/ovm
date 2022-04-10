from django.db import models
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phonenumber = PhoneNumberField(unique=True, null=True, blank=True, verbose_name='Telefoonnummer',
                                   help_text='Telefoonnummer in formaat +31612065956.')  # load as person.phoneNumber.as_e164 https://www.delftstack.com/howto/django/django-phone-number-field/
    dateofbirth = models.DateField(verbose_name='Geboortedatum', null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    verkeersregelaar = models.BooleanField(default=False)
    centralist = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #         super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)