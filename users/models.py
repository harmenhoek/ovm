from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phonenumber = PhoneNumberField(unique=True, null=True, blank=True) #load as person.phoneNumber.as_e164 https://www.delftstack.com/howto/django/django-phone-number-field/
    dateofbirth = models.DateField(null=True, blank=True)
    verkeersregelaar = models.BooleanField(default=False)
    centralist = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
#         super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
