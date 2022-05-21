from django.db import models
from django.utils import timezone
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.urls import reverse
import os
from simple_history.models import HistoricalRecords

class Log(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.RESTRICT, limit_choices_to={'is_superuser': False})
    added_on = models.DateTimeField(default=timezone.now)
    log = models.TextField()
    file1 = models.FileField(blank=True, null=True, verbose_name="Bestanden")
    file2 = models.FileField(blank=True, null=True, verbose_name="")
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