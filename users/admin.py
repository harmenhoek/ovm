from django.contrib import admin
from .models import CustomUser, UserSpecialism
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(CustomUser, SimpleHistoryAdmin)
admin.site.register(UserSpecialism, SimpleHistoryAdmin)

