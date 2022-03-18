from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    post_fullname = models.CharField(max_length=100, null=True, blank=True)
    post_abbr = models.CharField(max_length=5, null=True, blank=True)
    maplocation_x = models.IntegerField(null=True, blank=True, default=0)
    maplocation_y = models.IntegerField(null=True, blank=True, default=0)
    description = models.TextField(null=True, blank=True)
    verkeersregelaar = models.BooleanField(default=False)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.post_abbr

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

class Day(models.Model):
    date = models.DateField()
    dayname = models.CharField(max_length=15)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

class Shift(models.Model):
    shiftname = models.CharField(max_length=10)
    date = models.ForeignKey(Day, on_delete=models.SET_NULL, null=True, blank=True)
    shiftstart = models.TimeField()
    shiftend = models.TimeField()
    shiftstart_extra = models.DurationField()
    shiftend_extra = models.DurationField()


class Planning(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customstart = models.TimeField(null=True, blank=True)
    customend = models.TimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)