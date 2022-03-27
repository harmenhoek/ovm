from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Flag(models.Model):
    flag = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=100, default='bug', help_text='Set a icon from <a target="_blank" href="https://fontawesome.com/icons?m=free">this library</a>.')
    # history = HistoricalRecords()

    def __str__(self):
        return self.flag

class Post(models.Model):
    post_fullname = models.CharField(max_length=100, null=True, blank=True)
    postslug = models.SlugField(max_length=5, null=True, blank=True)
    maplocation_x = models.FloatField(null=True, blank=True, default=0)
    maplocation_y = models.FloatField(null=True, blank=True, default=0)
    description = models.TextField(null=True, blank=True)
    verkeersregelaar = models.BooleanField(default=False)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    flag = models.ForeignKey(Flag, on_delete=models.SET_NULL, null=True, blank=True)
    flag_comment = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.postslug

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Day(models.Model):
    date = models.DateField()
    dayname = models.CharField(max_length=15)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.dayname} ({self.date})"

class Shift(models.Model):
    shiftname = models.CharField(max_length=10)
    date = models.ForeignKey(Day, on_delete=models.SET_NULL, null=True, blank=True)
    shiftstart = models.TimeField()
    shiftend = models.TimeField()
    shiftstart_extra = models.DurationField()
    shiftend_extra = models.DurationField()

    def __str__(self):
        return f"{self.shiftname} ({self.date.dayname} {self.shiftstart.strftime('%H:%M')}-{self.shiftend.strftime('%H:%M')})"


class Planning(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customstart = models.TimeField(null=True, blank=True)
    customend = models.TimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    remove = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.post} - {self.shift.shiftname} | {self.user}  - confirmed: {self.confirmed}"