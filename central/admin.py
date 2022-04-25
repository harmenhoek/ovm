from django.contrib import admin
from .models import Post, ShiftDay, ShiftTime, Planning

# Register your models here.
admin.site.register(Post)
admin.site.register(ShiftDay)
admin.site.register(ShiftTime)
admin.site.register(Planning)
