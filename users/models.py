from django.db import models
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import os
import time
from PIL import Image, ExifTags


class CustomUser(AbstractUser):
    phonenumber = PhoneNumberField(unique=True, null=True, blank=True, verbose_name='Telefoonnummer',
                                   help_text='Telefoonnummer in formaat +31612065956.')  # load as person.phoneNumber.as_e164 https://www.delftstack.com/howto/django/django-phone-number-field/
    dateofbirth = models.DateField(verbose_name='Geboortedatum', null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics', blank=True)
    verkeersregelaar = models.BooleanField(default=False)
    centralist = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        maxsize = 1000
        if self.image:
            self.image = process_image(self.image.path, self.pk, maxsize, media_folder='profile_pics')
            super().save(*args, **kwargs)
        else:
            self.image = 'default.png'
            super().save(*args, **kwargs)




            # form.instance.username = f"{form.instance.first_name.lower()}{form.instance.last_name.lower()}"

def process_image(path, pk, maxsize, media_folder='item_pics'):
# Function does 3 things:
# 1. Rotate image by EXIF (needed since this info is lost by the PIL process)
# 2. Crop image to thumbnail of maxsize
# 3. Rename image (since image is already saved, we save the loaded PIL image with new name and remove the old one).

    image = Image.open(path)
    # Rotate image by EXIF
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6:
            image = image.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8:
            image = image.transpose(Image.ROTATE_90)
    except:  # image has no EXIF
        pass

    # Crop image
    if image.height > maxsize or image.width > maxsize:  # TODO move this to views?!
        output_size = (maxsize, maxsize)
        image.thumbnail(output_size)

    # Rename image (since already saved, we delete original one, save a new one)
    path_dir = os.path.dirname(path)
    ext = os.path.splitext(path)[1] #.JPG
    shorthash = hash(time.time())
    path_new = os.path.join(path_dir, str(pk) + '_' + str(shorthash) + ext)
    image.save(path_new)
    os.remove(path)
    path_new_full: str = os.path.join(media_folder + '/', str(pk) + '_' + str(shorthash) + ext)

    return path_new_full