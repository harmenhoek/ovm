from django.db import models
from django.utils import timezone
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.urls import reverse
from simple_history.models import HistoricalRecords

class Flag(models.Model):
    flag = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=100, default='bug', help_text='Set a icon from <a target="_blank" href="https://fontawesome.com/icons?m=free">this library</a>.')
    history = HistoricalRecords()

    def __str__(self):
        return self.flag

class Post(models.Model):
    post_fullname = models.CharField(max_length=100, null=True, blank=True)
    postslug = models.SlugField(max_length=5, null=True, blank=True, unique=True)
    maplocation_x = models.FloatField(null=True, blank=True, default=0)
    maplocation_y = models.FloatField(null=True, blank=True, default=0)
    description = models.TextField(null=True, blank=True)
    verkeersregelaar = models.BooleanField(default=False)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    flag = models.ForeignKey(Flag, on_delete=models.SET_NULL, null=True, blank=True)
    flag_comment = models.CharField(max_length=100, null=True, blank=True)
    history = HistoricalRecords()


    def __str__(self):
        return self.postslug

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class ShiftDay(models.Model):
    date = models.DateField(verbose_name="Datum")
    dayname = models.SlugField(max_length=15, verbose_name="Dag")
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True, verbose_name="Extra info dag")

    def __str__(self):
        return f"{self.dayname} ({self.date})"

class ShiftTime(models.Model):
    timestart = models.TimeField()
    timeend = models.TimeField()
    timename = models.IntegerField(help_text='Number of the shift')
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Shift {self.timename} ({self.timestart} - {self.timeend})"


class Planning(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Post')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Persoon')
    starttime = models.TimeField(null=True, blank=True, verbose_name='Starttijd')
    endtime = models.TimeField(null=True, blank=True, verbose_name='Eindtijd')
    date = models.DateField(null=True, blank=True, verbose_name='Datum')
    comment = models.TextField(null=True, blank=True, verbose_name='Opmerking(en)')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='planning_created_by')
    confirmed = models.BooleanField(default=False, verbose_name='Bevestigd')
    confirmed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='planning_confirmed_by')
    removed = models.BooleanField(default=False, verbose_name='Verwijderd')
    removed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='planning_removed_by')
    signed_off = models.BooleanField(default=False, verbose_name='Afgemeld')
    signed_off_time = models.DateTimeField(null=True, blank=True, verbose_name='Afmeldtijd')
    signed_off_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='signed_of_by')
    copy_of = models.IntegerField(null=True, blank=True)
    external = models.BooleanField(default=False, verbose_name='Externe verkeersregelaar', help_text='Kan op meerdere posten staan en wordt automatisch bevestigd en afgemeld van post.')
    porto = models.BooleanField(default=False, verbose_name="Portofoon")
    bike = models.CharField(null=True, blank=True, max_length=100, verbose_name="Fietsnummer")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.pk} -- post {self.post} | {self.user}  - confirmed: {self.confirmed} - deleted: {self.removed} - signedoff: {self.signed_off}"