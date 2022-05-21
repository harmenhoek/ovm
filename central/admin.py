from django.contrib import admin
from .models import Post, ShiftDay, ShiftTime, Planning
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
admin.site.register(Post, SimpleHistoryAdmin)
admin.site.register(ShiftDay, SimpleHistoryAdmin)
admin.site.register(ShiftTime, SimpleHistoryAdmin)
admin.site.register(Planning, SimpleHistoryAdmin)
