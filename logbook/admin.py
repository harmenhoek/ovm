from django.contrib import admin
from .models import Log
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Log, SimpleHistoryAdmin)
