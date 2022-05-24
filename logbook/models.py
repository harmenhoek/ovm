from django.db import models
from django.utils import timezone
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.urls import reverse
import os
from simple_history.models import HistoricalRecords
from PIL import Image, ExifTags
import time

class Log(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.RESTRICT, limit_choices_to={'is_superuser': False})
    added_on = models.DateTimeField(default=timezone.now)
    log = models.TextField()
    file1 = models.FileField(blank=True, null=True, verbose_name="Bestanden", upload_to='log_files')
    file2 = models.FileField(blank=True, null=True, verbose_name="", upload_to='log_files')
    deleted = models.BooleanField(default=False)
    history = HistoricalRecords()

    def get_absolute_url(self):
        return reverse('log-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.pk} - {self.added_on} - {self.added_by}"

    def file1_extension(self):
        name, extension = os.path.splitext(self.file1.name)
        return extension

    def file2_extension(self):
        name, extension = os.path.splitext(self.file2.name)
        return extension

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # initial save (incl image)
        maxsize = 1200
        if self.file1:
            self.file1 = process_image(self.file1.path, self.pk, maxsize, media_folder='log_files')
            super().save(*args, **kwargs)
        if self.file2:
            self.file2 = process_image(self.file2.path, self.pk, maxsize, media_folder='log_files')
            super().save(*args, **kwargs)

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