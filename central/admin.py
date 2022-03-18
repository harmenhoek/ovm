from django.contrib import admin
from .models import Post, Day, Shift, Planning

# Register your models here.
admin.site.register(Post)
admin.site.register(Day)
admin.site.register(Shift)
admin.site.register(Planning)
