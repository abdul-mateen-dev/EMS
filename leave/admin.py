from django.contrib import admin

from .models import Leave,LeaveCategory
admin.site.register(Leave)
admin.site.register(LeaveCategory)